# -*- coding: utf-8 -*-

import os
import re
import sys
from java.sql import SQLException
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.crypto import CryptoUtils
from utils.tsk_file import TSKFileUtils
from utils.timestamp import TimestampUtils
from utils.module import VERSION, MODULE_WEB_COOKIES


class SteamDeckWebCookiesFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_WEB_COOKIES)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting cookie database from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckWebCookiesFIM()


class SteamDeckWebCookiesFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckWebCookiesFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_WEB_COOKIE_NAME,
                ArtifactUtils.ATTR_WEB_COOKIE_VALUE,
                ArtifactUtils.ATTR_WEB_COOKIE_HOST,
                ArtifactUtils.ATTR_WEB_COOKIE_PATH,
                ArtifactUtils.ATTR_WEB_COOKIE_IS_SECURE,
                ArtifactUtils.ATTR_WEB_COOKIE_IS_HTTPONLY,
                ArtifactUtils.ATTR_WEB_COOKIE_IS_PERSISTENT,
                ArtifactUtils.ATTR_WEB_COOKIE_HAS_EXPIRES,
                ArtifactUtils.ATTR_WEB_COOKIE_SAMESITE,
                ArtifactUtils.ATTR_WEB_COOKIE_CREATION_UTC,
                ArtifactUtils.ATTR_WEB_COOKIE_EXPIRES_UTC,
                ArtifactUtils.ATTR_WEB_COOKIE_LAST_ACCESS_UTC,
                ArtifactUtils.ATTR_WEB_COOKIE_PRIORITY,
                ArtifactUtils.ATTR_WEB_COOKIE_SOURCE_SCHEME,
            ]
        )

    def process(self, file):
        # skip non-files and slack files
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

        if re.search(r'deck\/\.local\/share\/Steam\/config\/htmlcache\/Cookies$', fpath):
            data.extend(self.__parse_cookies_db(file))
        
        return data

    def __parse_cookies_db(self, file):
        data = []

        fh = None
        dbConn = None
        stmt = None

        try:
            dbConn, fh = TSKFileUtils.open_sqlite_file(file, case=self.case)
        except SQLException as e:
            self.log(msg=file.getUniquePath(), error=e)

        if dbConn:

            dict_cols_mapping = {
                'name': ArtifactUtils.ATTR_WEB_COOKIE_NAME,
                'value': ArtifactUtils.ATTR_WEB_COOKIE_VALUE,
                'host_key': ArtifactUtils.ATTR_WEB_COOKIE_HOST,
                'path': ArtifactUtils.ATTR_WEB_COOKIE_PATH,
                'is_secure': ArtifactUtils.ATTR_WEB_COOKIE_IS_SECURE,
                'is_httponly': ArtifactUtils.ATTR_WEB_COOKIE_IS_HTTPONLY,
                'samesite': ArtifactUtils.ATTR_WEB_COOKIE_SAMESITE,
                'has_expires': ArtifactUtils.ATTR_WEB_COOKIE_HAS_EXPIRES,
                'creation_utc': ArtifactUtils.ATTR_WEB_COOKIE_CREATION_UTC,
                'expires_utc': ArtifactUtils.ATTR_WEB_COOKIE_EXPIRES_UTC,
                'last_access_utc': ArtifactUtils.ATTR_WEB_COOKIE_LAST_ACCESS_UTC,
                'is_persistent': ArtifactUtils.ATTR_WEB_COOKIE_IS_PERSISTENT,
                'priority': ArtifactUtils.ATTR_WEB_COOKIE_PRIORITY,
                'source_scheme': ArtifactUtils.ATTR_WEB_COOKIE_SOURCE_SCHEME,
                'encrypted_value': ArtifactUtils.ATTR_WEB_COOKIE_ENCRYPTED_VALUE,
            }

            try:
                stmt = dbConn.createStatement()
                results = stmt.executeQuery("SELECT * FROM cookies;")
                while results.next():
                    d = self.get_data_template()

                    for col, key in dict_cols_mapping.items():
                        try:
                            if col == "encrypted_value":
                                d[key] = results.getBytes(col)
                                d[key] = CryptoUtils.decrypt_chrome_secrets_linux_v10(d[key])
                            elif col in ["creation_utc", "expires_utc", "last_access_utc"]:
                                d[key] = TimestampUtils.webkit_to_date_str(
                                    results.getString(col))
                            else:
                                d[key] = results.getString(col)
                        except Exception as e:
                            d[key] = ArtifactUtils.ERR_PARSE

                            self.log(msg="{} >> col={} >> key={}".format(file.getUniquePath(), col, key), error=e)

                    try:
                        val_enc = d[ArtifactUtils.ATTR_WEB_COOKIE_ENCRYPTED_VALUE]
                        val = d[ArtifactUtils.ATTR_WEB_COOKIE_VALUE]
                        if val == "" and val_enc != "":
                            d[ArtifactUtils.ATTR_WEB_COOKIE_VALUE] = \
                                d[ArtifactUtils.ATTR_WEB_COOKIE_ENCRYPTED_VALUE]
                    except Exception as e:
                        self.log(msg=file.getUniquePath(), error=e)

                    data.append(d)

            except SQLException as e:
                self.log(msg=file.getUniquePath(), error=e)

        TSKFileUtils.close_sqlite_file(dbConn, fh)

        return data
