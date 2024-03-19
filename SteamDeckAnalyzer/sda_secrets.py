# -*- coding: utf-8 -*-

import os
import re
import sys
import json
from java.sql import SQLException
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_SECRETS


class SteamDeckSecretsFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_SECRETS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting secrets and tokens from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckSecretsFIM()


class SteamDeckSecretsFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckSecretsFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_SECRET_KIND,
                ArtifactUtils.ATTR_SECRET_CONTEXT,
                ArtifactUtils.ATTR_SECRET_IDENTITY,
                ArtifactUtils.ATTR_SECRET_SECRET,
                ArtifactUtils.ATTR_SECRET_DESC,
            ]
        )

    def process(self, file):
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # process files that are of interest
        try:
            data = self.__process(file)
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
            return IngestModule.ProcessResult.ERROR

        # create and post artifact(s) on blackboard, if not already existing
        for d in data:
            self.make_blackboard_artifact(file, d)

        return IngestModule.ProcessResult.OK

    def __process(self, file):
        data = []
        fpath = file.getUniquePath()

        if re.search(r'\.pki\/nssdb\/key\d+\.db$', fpath):
            data.extend(self.__parse_key_db(file))

        elif re.search(r'deck\/\.netrc$', fpath) \
            or re.search(r'\.steamos\/offload\/root\/\.netrc$', fpath):
            data.extend(self.__parse_netrc(file))

        elif re.search(r'\.local\/share\/Steam\/userdata\/\d+\/config\/localconfig\.vdf$', fpath):
            data.extend(self.__parse_localconfig_vdf(file))
        
        elif re.search(r'usr\/share\/accounts\/providers\/kde\/opendesktop\.provider$', fpath):
            data.extend(self.__parse_opendesktop_provider(file))
        
        elif re.search(r'\.steam\/steam\.token$', fpath):
            data.extend(self.__parse_steam_token(file))
        
        elif re.search(r'\.local\/share\/Steam\/config\/htmlcache\/UserPrefs\.json$', fpath):
            data.extend(self.__parse_userprefs(file))

        return data
    
    def __parse_userprefs(self, file):
        data = []

        fh = None
        try:
            fh = TSKFileUtils.open_file(file=file, case=self.case)
            d = json.load(fh)
            if 'media' in d:
                if 'device_id_salt' in d['media']:
                    item = {}
                    item[ArtifactUtils.ATTR_SECRET_KIND] = 'Device ID Salt'
                    item[ArtifactUtils.ATTR_SECRET_CONTEXT] = 'Steam HTML Cache'
                    item[ArtifactUtils.ATTR_SECRET_SECRET] = \
                        str(d['media']['device_id_salt'].strip())
                    item[ArtifactUtils.ATTR_SECRET_DESC] = \
                        'User Prefs > Media > Device ID Salt'
                    data.append(item)

        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)

        TSKFileUtils.close_file(fh)

        return data
    
    def __parse_key_db(self, file):
        data = []

        fh = None
        dbConn = None
        stmt = None

        try:
            dbConn, fh = TSKFileUtils.open_sqlite_file(file, case=self.case)
        except SQLException as e:
            self.log(msg=file.getUniquePath(), error=e)

        if dbConn:
            try:
                stmt = dbConn.createStatement()
                results = stmt.executeQuery("SELECT * FROM metaData;")
                while results.next():

                    try:
                        id_ = results.getString("id")
                    except Exception as e:
                        id_ = ArtifactUtils.ERR_PARSE
                        self.log(msg="{} >> id".format(file.getUniquePath()), error=e)
                    
                    try:
                        i1 = results.getString("item1")
                        i1 = '{}'.format(ArtifactUtils.ERR_BLOB) \
                            if isinstance(i1, unicode) else str(i1)
                    except Exception as e:
                        i1 = ArtifactUtils.ERR_PARSE
                        self.log(msg="{} >> item1".format(file.getUniquePath()), error=e)
                    
                    try:
                        i2 = results.getString("item2")
                        i2 = '{}'.format(ArtifactUtils.ERR_BLOB) \
                            if isinstance(i2, unicode) else str(i2)
                    except Exception as e:
                        i2 = ArtifactUtils.ERR_PARSE
                        self.log(msg="{} >> item2".format(file.getUniquePath()), error=e)

                    d = self.get_data_template()
                    d[ArtifactUtils.ATTR_SECRET_KIND] = "{}".format(id_.title())
                    d[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Network Security Services"
                    d[ArtifactUtils.ATTR_SECRET_SECRET] = i1
                    d[ArtifactUtils.ATTR_SECRET_DESC] = "item1"
                    data.append(d)

                    d = self.get_data_template()
                    d[ArtifactUtils.ATTR_SECRET_KIND] = "{}".format(id_.title())
                    d[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Network Security Services"
                    d[ArtifactUtils.ATTR_SECRET_SECRET] = i2
                    d[ArtifactUtils.ATTR_SECRET_DESC] = "item2"
                    data.append(d)

            except SQLException as e:
                self.log(msg=file.getUniquePath(), error=e)

        TSKFileUtils.close_sqlite_file(dbConn, fh)

        return data

    def __parse_netrc(self, file):
        items = []

        fh = None
        try:
            fh = TSKFileUtils.open_file(file, case=self.case)

            for line in fh.readlines():

                try:
                    l = line.strip()
                    if not l:
                        continue
                    l = re.sub(r'^machine\s+', '', l).strip()
                    m = re.match(r'^([^\s]*)\s+login\s+(.*)\s+password\s+(.*)$', l)
                    assert m and len(m.groups()) == 3, \
                        "{} >> {}".format(line, m.groups() if m else '')
                    infos = list(m.groups())

                    d = self.get_data_template()
                    d[ArtifactUtils.ATTR_SECRET_KIND] = "Credentials"
                    d[ArtifactUtils.ATTR_SECRET_CONTEXT] = infos[0]
                    d[ArtifactUtils.ATTR_SECRET_IDENTITY] = infos[1]
                    d[ArtifactUtils.ATTR_SECRET_SECRET] = infos[2]
                    items.append(d)

                except Exception as e:
                    self.log(msg="{} >> {}".format(file.getUniquePath, line), error=e)

        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
        
        finally:
            TSKFileUtils.close_file(fh)

        return items

    def __parse_localconfig_vdf(self, file):
        items = []

        #

        try:
            dict_localconfig = TSKFileUtils.parse_vdf_file(file, case=self.case)
            assert "UserLocalConfigStore" in dict_localconfig, \
                "{} > {}".format(sorted(dict_localconfig.keys()), dict_localconfig)
            data = dict_localconfig["UserLocalConfigStore"]
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)

        #

        d = self.get_data_template()
        d[ArtifactUtils.ATTR_SECRET_KIND] = "Key"
        d[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Steam Cloud"
        try:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = data["CloudKey"]
        except:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = ArtifactUtils.ERR_PARSE
        items.append(d)

        #

        d = self.get_data_template()
        d[ArtifactUtils.ATTR_SECRET_KIND] = "CRC"
        d[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Steam Cloud"
        try:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = data["CloudKeyCRC"]
        except:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = ArtifactUtils.ERR_PARSE
        items.append(d)

        #

        d = self.get_data_template()
        d[ArtifactUtils.ATTR_SECRET_KIND] = "Token"
        d[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Steam Shared Auth"
        try:
            d[ArtifactUtils.ATTR_SECRET_IDENTITY] = data["SharedAuth"]["id"]
        except:
            d[ArtifactUtils.ATTR_SECRET_IDENTITY] = ArtifactUtils.ERR_PARSE
        try:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = data["SharedAuth"]["AuthData"]
        except:
            d[ArtifactUtils.ATTR_SECRET_SECRET] = ArtifactUtils.ERR_PARSE
        items.append(d)

        #
        
        return items

    def __parse_steam_token(self, file):
        data = self.get_data_template()
        data[ArtifactUtils.ATTR_SECRET_KIND] = "Token"
        data[ArtifactUtils.ATTR_SECRET_CONTEXT] = "Steam"

        fh = None
        try:
            fh = TSKFileUtils.open_file(file)
            data[ArtifactUtils.ATTR_SECRET_SECRET] = fh.read().strip()
        except Exception as e:
            data[ArtifactUtils.ATTR_SECRET_SECRET] = ArtifactUtils.ERR_PARSE
            self.log(msg=file.getUniquePath(), error=e)
            
        finally:
            TSKFileUtils.close_file(fh)
        
        return [data]

    def __parse_opendesktop_provider(self, file):
        data = self.get_data_template()
        data[ArtifactUtils.ATTR_SECRET_KIND] = "Token"

        try:
            tree = TSKFileUtils.parse_xml_file(file, case=self.case)

            # context
            try:
                data[ArtifactUtils.ATTR_SECRET_CONTEXT] = vars(tree.find('.//name'))['text'].strip()
            except:
                data[ArtifactUtils.ATTR_SECRET_CONTEXT] = ArtifactUtils.ERR_PARSE

            # description
            try:
                nodes = [vars(n) for n in tree.findall('.//setting')]
                for n in nodes:
                    if n["attrib"]["name"] == "method":
                        method = n["text"].strip()
                        break
            except:
                method = ""
            
            try:
                data[ArtifactUtils.ATTR_SECRET_DESC] = \
                    vars(tree.find('.//description'))['text'].strip()
                if method:
                    data[ArtifactUtils.ATTR_SECRET_DESC] = \
                        "{}; {}".format(method, data[ArtifactUtils.ATTR_SECRET_DESC])
            except:
                data[ArtifactUtils.ATTR_SECRET_DESC] = ArtifactUtils.ERR_PARSE

            # identity
            try:
                nodes = [vars(n) for n in tree.findall('.//setting')]
                for n in nodes:
                    if n["attrib"]["name"] == "ClientId":
                        data[ArtifactUtils.ATTR_SECRET_IDENTITY] = n["text"].strip()
                        break
            except Exception as e:
                data[ArtifactUtils.ATTR_SECRET_IDENTITY] = ArtifactUtils.ERR_PARSE

            # secret
            try:
                nodes = [vars(n) for n in tree.findall('.//setting')]
                for n in nodes:
                    if n["attrib"]["name"] == "ClientSecret":
                        data[ArtifactUtils.ATTR_SECRET_SECRET] = n["text"].strip()
                        break
            except Exception as e:
                data[ArtifactUtils.ATTR_SECRET_SECRET] = ArtifactUtils.ERR_PARSE

        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
        
        return [data]
