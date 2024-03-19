# -*- coding: utf-8 -*-

import os
import re
import sys
from collections import OrderedDict
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_FRIENDS


class SteamDeckFriendsFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_FRIENDS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting friends from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckFriendsFIM()


class SteamDeckFriendsFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckFriendsFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_FRIEND_ID,
                ArtifactUtils.ATTR_NAME,
                ArtifactUtils.ATTR_NAME_HISTORY,
            ]
        )

    def process(self, file):
        # skip non-files and slack files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # skip files that are not of interest
        if file.getName() != 'localconfig.vdf':
            return IngestModule.ProcessResult.OK
        
        # extract friends from `localconfig.vdf`
        friends = self.parse_localconfig_vdf(TSKFileUtils.parse_vdf_file(file))

        # create and post artifact(s) on blackboard, if not already existing
        for data in friends:
            self.make_blackboard_artifact(file, data)

        return IngestModule.ProcessResult.OK

    def parse_localconfig_vdf(self, dict_localconfig):
        assert isinstance(dict_localconfig, OrderedDict) or isinstance(dict_localconfig, dict), \
            "{}: {}".format(type(dict_localconfig), dict_localconfig)
        assert "UserLocalConfigStore" in dict_localconfig, \
            "{} > {}".format(sorted(dict_localconfig.keys()), dict_localconfig)
        data = dict_localconfig["UserLocalConfigStore"]
        assert "friends" in data, "{} > {}".format(sorted(data.keys()), data)
        data = data["friends"]

        friends = []
        for k, v in data.items():
            if not re.match(r"\d+", k):
                continue
            if "NameHistory" not in v:
                continue

            friends.append({
                ArtifactUtils.ATTR_FRIEND_ID: str(k),
                ArtifactUtils.ATTR_NAME: str(v['name']) if 'name' in v else '',
                ArtifactUtils.ATTR_NAME_HISTORY: ', '.join(v['NameHistory'].values()) if 'NameHistory' in v else '',
                ArtifactUtils.ATTR_AVATAR: str(v['avatar']) if 'avatar' in v else '',
            })
        
        return friends