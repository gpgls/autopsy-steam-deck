# -*- coding: utf-8 -*-

import os
import re
import sys
import json
from collections import OrderedDict
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import DataSourceIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.timestamp import TimestampUtils
from utils.module import VERSION, MODULE_USERS


class SteamDeckUsersDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_USERS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting users from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckUsersDSIM()


class SteamDeckUsersDSIM(DataSourceIngestModulePlus):

    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self,
            SteamDeckUsersDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_STEAM_ID,
                ArtifactUtils.ATTR_FRIEND_ID,
                ArtifactUtils.ATTR_ACCOUNT_NAME,
                ArtifactUtils.ATTR_PERSONA_NAME,
                ArtifactUtils.ATTR_LASTLOGIN_DATE,
                ArtifactUtils.ATTR_AUTO_LOGIN_USER,
                ArtifactUtils.ATTR_ALLOW_AUTO_LOGIN,
                ArtifactUtils.ATTR_MOST_RECENT,
                ArtifactUtils.ATTR_REMEMBER_PASSWORD,
                ArtifactUtils.ATTR_WANTS_OFFLINE_MODE,
                ArtifactUtils.ATTR_SKIP_OFFLINE_MODE_WARNING,
                ArtifactUtils.ATTR_LASTLOGIN,
                ArtifactUtils.ATTR_SOURCES,
            ]
        )

    def startUp(self, context):
        DataSourceIngestModulePlus.startUp(self, context)

    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be by pre-filtering files
        self.files = self.fileManager.findFiles(dataSource, "%.vdf")

        # update the progress bar
        self.update_progress()

        sources = {}
        for file in self.files:
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            # skip non-files, slack files, journal files
            if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
                continue

            if file.getName() == 'loginusers.vdf':
                sources[file.getUniquePath()] = \
                    self.__parse_loginusers_vdf(TSKFileUtils.parse_vdf_file(file))
                
            elif file.getName() == 'localconfig.vdf':
                sources[file.getUniquePath()] = \
                    self.__parse_localconfig_vdf(TSKFileUtils.parse_vdf_file(file))
            
            elif file.getName() == 'registry.vdf':
                user = self.__parse_registry_vdf(TSKFileUtils.parse_vdf_file(file))
                if user:
                    sources[file.getUniquePath()] = user

        # update the progress bar
        self.update_progress()

        # aggregate user information found in different sources
        users = self.__aggregate(sources)
        
        # create and post artifact(s) on blackboard, if not already existing
        mockfile = self.get_mockup_file_for_multifile_artifacts(dataSource)

        for _, data in users.items():
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            self.make_blackboard_artifact(mockfile, data)
            self.update_progress()

        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK

    def __aggregate(self, sources):
        users = {}

        autologin_user = None
        autologin_user_source = None
        for key, sourcedata in sources.items():
            if key.endswith('registry.vdf') and autologin_user is None:
                autologin_user = "{}".format(sourcedata)
                autologin_user_source = key

        for key in [_ for _ in sources.keys() if _.endswith('loginusers.vdf')]:
            for user_id, userdata_ in sources[key].items():
                userdata = dict(userdata_)
                
                if autologin_user:
                    userdata[ArtifactUtils.ATTR_AUTO_LOGIN_USER] = str(
                        (userdata[ArtifactUtils.ATTR_ACCOUNT_NAME] == autologin_user) \
                        or (userdata[ArtifactUtils.ATTR_PERSONA_NAME] == autologin_user))
        
                userdata[ArtifactUtils.ATTR_SOURCES] = set()
                userdata[ArtifactUtils.ATTR_SOURCES].add(key)
                if autologin_user_source:
                    userdata[ArtifactUtils.ATTR_SOURCES].add(autologin_user_source)

                if user_id not in users:
                    users[user_id] = userdata
                else:
                    self.log("FOUND DUPLICATE >> {} >> {} >> {}".format(key, users[user_id], userdata))

        for key in [_ for _ in sources.keys() if _.endswith('localconfig.vdf')]:
            for _, userdata in users.items():
                if ArtifactUtils.ATTR_FRIEND_ID not in userdata:
                    added = False
                    if userdata[ArtifactUtils.ATTR_PERSONA_NAME] in sources[key]:
                        added = True
                        userdata[ArtifactUtils.ATTR_FRIEND_ID] = \
                            sources[key][userdata[ArtifactUtils.ATTR_PERSONA_NAME]]
                    elif userdata[ArtifactUtils.ATTR_ACCOUNT_NAME] in sources[key]:
                        added = True
                        userdata[ArtifactUtils.ATTR_FRIEND_ID] = \
                            sources[key][userdata[ArtifactUtils.ATTR_ACCOUNT_NAME]]
                    if added:
                        userdata[ArtifactUtils.ATTR_SOURCES].add(key)

        for _, userdata in users.items():
            assert ArtifactUtils.ATTR_SOURCES in userdata, \
                "{}".format(json.dumps(userdata, indent=4))
            assert isinstance(userdata[ArtifactUtils.ATTR_SOURCES], set), \
                "{}: {}".format(type(userdata), userdata)
            userdata[ArtifactUtils.ATTR_SOURCES] = \
                "; ".join(sorted(userdata[ArtifactUtils.ATTR_SOURCES]))

        return users
    
    def __parse_registry_vdf(self, dict_registry):
        assert isinstance(dict_registry, OrderedDict) or isinstance(dict_registry, dict), \
            "{}".format(type(dict_registry))
        data = dict(dict_registry)

        for key in ["Registry", "HKCU", "Software", "Valve", "Steam"]:
            assert key in data, "{} > {}".format(key, sorted(data[key].keys()))
            data = data[key]
        if "AutoLoginUser" in data:
            return str(data["AutoLoginUser"])

        return ""

    def __parse_localconfig_vdf(self, dict_localconfig):
        assert isinstance(dict_localconfig, OrderedDict) or isinstance(dict_localconfig, dict), \
            "{}: {}".format(type(dict_localconfig), dict_localconfig)
        assert "UserLocalConfigStore" in dict_localconfig, \
            "{} > {}".format(sorted(dict_localconfig.keys()), dict_localconfig)
        data = dict_localconfig["UserLocalConfigStore"]
        assert "friends" in data, "{} > {}".format(sorted(data.keys()), data)
        data = data["friends"]

        dict_names_to_friend_id = {}
        for k, v in data.items():
            if not re.match(r"\d+", k):
                continue
            if "NameHistory" not in v:
                continue

            friend_id = str(k)
            
            if 'name' in v and v['name'] not in dict_names_to_friend_id:
                dict_names_to_friend_id[v['name']] = friend_id
            if 'NameHistory' in v:
                for _, name in v['NameHistory'].items():
                    if name not in dict_names_to_friend_id:
                        dict_names_to_friend_id[name] = friend_id
                    
        return dict_names_to_friend_id

    def __parse_loginusers_vdf(self, dict_loginusers):
        assert "users" in dict_loginusers.keys(), "{}".format(sorted(dict_loginusers.keys()))

        renamings = {
            "AccountName": ArtifactUtils.ATTR_ACCOUNT_NAME,
            "PersonaName": ArtifactUtils.ATTR_PERSONA_NAME,
            "Timestamp": ArtifactUtils.ATTR_LASTLOGIN,
            "MostRecent": ArtifactUtils.ATTR_MOST_RECENT,
            "AllowAutoLogin": ArtifactUtils.ATTR_ALLOW_AUTO_LOGIN,
            "RememberPassword": ArtifactUtils.ATTR_REMEMBER_PASSWORD,
            "WantsOfflineMode": ArtifactUtils.ATTR_WANTS_OFFLINE_MODE,
            "SkipOfflineModeWarning": ArtifactUtils.ATTR_SKIP_OFFLINE_MODE_WARNING,
        }

        dict_users = {}
        for steam_id, userdata in dict_loginusers["users"].items():
            user = {ArtifactUtils.ATTR_STEAM_ID: steam_id}
            for old_key, new_key in renamings.items():
                if old_key in userdata:
                    user[new_key] = userdata[old_key]
            
            if ArtifactUtils.ATTR_LASTLOGIN in user:
                user[ArtifactUtils.ATTR_LASTLOGIN_DATE] = \
                    TimestampUtils.epoch_to_date_str(user[ArtifactUtils.ATTR_LASTLOGIN])

            dict_users[steam_id] = user

        return dict_users
