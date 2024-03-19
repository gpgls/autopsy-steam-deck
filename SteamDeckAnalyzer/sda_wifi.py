# -*- coding: utf-8 -*-

import os
import re
import sys
import json
from itertools import chain
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_WIFI


class SteamDeckWiFiFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_WIFI)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting Wi-Fi credentials from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckWiFiFIM()


class SteamDeckWiFiFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckWiFiFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_SSID,
                ArtifactUtils.ATTR_PASSWORD,
                ArtifactUtils.ATTR_8021X_IDENTITY,
                ArtifactUtils.ATTR_OTHER,
            ]
        )

    def process(self, file):
        # skip non-files, and slack files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # skip non-relevant files
        if not re.search(r"([^\/]*)\.(nmconnection|8021x|psk)", file.getName()):
            return IngestModule.ProcessResult.OK

        # parse contents from file object
        data = {}
        for attr in self.attributes:
            data[attr] = ""

        error = False
        if file.getNameExtension().startswith('nmconnection'):
            data.update(self._parse_nmconnection(file))
        else:
            fh = TSKFileUtils.open_file(file)
            if file.getNameExtension().startswith('8021x'):
                data.update(self._parse_8021x(fh))
            elif file.getNameExtension().startswith('psk'):
                data.update(self._parse_psk(fh, file.getName()))
            else:
                error = True
            TSKFileUtils.close_file(fh)
        if error:
            self.log("Unexpected case: {}".format(file.getUniquePath()))
            return IngestModule.ProcessResult.ERROR

        if ArtifactUtils.ATTR_OTHER in data:
            data[ArtifactUtils.ATTR_OTHER] = json.dumps(data[ArtifactUtils.ATTR_OTHER])

        # create and post artifact on blackboard, if not already existing
        self.make_blackboard_artifact(file, data)

        return IngestModule.ProcessResult.OK
    
    def _parse_nmconnection(self, file):
        data = {}

        # extract SSID and password
        config = TSKFileUtils.parse_config_file(file)
        needles = {
            ArtifactUtils.ATTR_SSID: ['wifi_ssid', 'connection_id'],
            ArtifactUtils.ATTR_PASSWORD: ['802_1x_password', 'wifi_security_psk'],
            ArtifactUtils.ATTR_8021X_IDENTITY: ['802_1x_identity'],
        }
        for attr, keys in needles.items():
            for key in keys:
                if attr in data:
                    break
                if key in config:
                    data[attr] = config[key]

        # summarize remaining information as `other`
        data[ArtifactUtils.ATTR_OTHER] = {}
        ignores = list(chain.from_iterable(needles.values()))
        for key in config.keys():
            if key not in ignores and key not in data[ArtifactUtils.ATTR_OTHER]:
                data[ArtifactUtils.ATTR_OTHER][key] = config[key]

        return data

    def _parse_8021x(self, fh):
        data = { 
            ArtifactUtils.ATTR_OTHER: {}
        }

        for line in fh.readlines():
            l = line.strip()
            match = re.search(r'Auto-generated from NetworkManager connection "([^"]*)"', l)
            if match: 
                # example: # Auto-generated from NetworkManager connection "FAU.fm"
                data[ArtifactUtils.ATTR_SSID] = match.groups()[0]
            else:
                match = re.match(r'([^=]*)=(.*)', l.strip())
                if match:
                    assert len(match.groups()) == 2
                    key, value = match.groups()
                    k = key.lower()
                    if 'identity' in k and ArtifactUtils.ATTR_8021X_IDENTITY not in data:
                        data[ArtifactUtils.ATTR_8021X_IDENTITY] = value
                    elif 'password' in k and ArtifactUtils.ATTR_PASSWORD not in data:
                        data[ArtifactUtils.ATTR_PASSWORD] = value
                    else:
                        # summarize remaining information as `other`
                        data[ArtifactUtils.ATTR_OTHER][key] = value

        return data

    def _parse_psk(self, fh, file_name):
        data = {
            ArtifactUtils.ATTR_SSID: file_name,
            ArtifactUtils.ATTR_OTHER: {}
        }

        for line in fh.readlines():
            match = re.match(r'([^=]*)=(.*)', line.strip())
            if match:
                assert len(match.groups()) == 2
                key, value = match.groups()
                k = key.lower()
                if 'passphrase' in k and ArtifactUtils.ATTR_PASSWORD not in data:
                    data[ArtifactUtils.ATTR_PASSWORD] = value
                else:
                    # summarize remaining information as `other`
                    data[ArtifactUtils.ATTR_OTHER][key] = value
        
        return data
