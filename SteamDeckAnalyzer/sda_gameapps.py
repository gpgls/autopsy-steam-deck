# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import itertools
from collections import OrderedDict
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import DataSourceIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.timestamp import TimestampUtils
from utils.tsk_file import TSKFileUtils
from utils.steamcloud import SteamCloudUtils
from utils.module import VERSION, MODULE_GAMEAPPS


class SteamDeckGameAppsDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_GAMEAPPS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting games and apps from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckGameAppsDSIM()

class SteamDeckGameAppsDSIM(DataSourceIngestModulePlus):
    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self, 
            SteamDeckGameAppsDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_APP_ID,
                ArtifactUtils.ATTR_NAME,
                ArtifactUtils.ATTR_OWNER_STEAM_ID,
                ArtifactUtils.ATTR_AUTO_LOGIN_USER,
                ArtifactUtils.ATTR_INSTALLED,
                ArtifactUtils.ATTR_RUNNING,
                ArtifactUtils.ATTR_UPDATING,
                ArtifactUtils.ATTR_LASTPLAYED_DATE,
                ArtifactUtils.ATTR_AUTOCLOUD_LASTEXIT_DATE,
                ArtifactUtils.ATTR_AUTOCLOUD_LASTLAUNCH_DATE,
                ArtifactUtils.ATTR_LASTUPDATED_DATE,
                ArtifactUtils.ATTR_PLAYTIME,
                ArtifactUtils.ATTR_PLAYTIME_2WKS,
                ArtifactUtils.ATTR_CLOUD_LAST_SYNC_STATE,
                ArtifactUtils.ATTR_CLOUD_QUOTA_FILES,
                ArtifactUtils.ATTR_CLOUD_QUOTA_BYTES,
                ArtifactUtils.ATTR_CLOUD_USED_FILES,
                ArtifactUtils.ATTR_CLOUD_USED_BYTES,
                ArtifactUtils.ATTR_LASTPLAYED,
                ArtifactUtils.ATTR_LASTUPDATED,
                ArtifactUtils.ATTR_AUTOCLOUD_LASTEXIT,
                ArtifactUtils.ATTR_AUTOCLOUD_LASTLAUNCH,
                ArtifactUtils.ATTR_FILE_PATH
            ]
        )

        self.app_ids_names = {}

    
    def startUp(self, context):
        DataSourceIngestModulePlus.startUp(self, context)

        dir_plugin = os.path.dirname(os.path.abspath(__file__))
        dir_assets = os.path.join(dir_plugin, "assets")

        # fetch AppID-to-Name dictionary from online source, or read it from disk
        file_apps_latest = os.path.join(dir_assets, "apps_latest.json")
        if SteamCloudUtils.download_app_dictionary(filepath=file_apps_latest):
            self.log("Fetched latest app dictionary from online source.")
            with open(file_apps_latest, 'r') as f:
                self.app_ids_names = json.load(f)
        else:
            self.log("Fetched historic app dictionary from disk.")
            with open(os.path.join(dir_assets, "apps_default.json"), 'r') as f:
                self.app_ids_names = json.load(f)

        # conduct sanity checks
        assert isinstance(self.app_ids_names, dict), \
            "{}: {}".format(type(self.app_ids_names), self.app_ids_names)
        assert len(self.app_ids_names) > SteamCloudUtils.SANITY_CHECK_MIN_APP_COUNT, \
            "{}".format(len(self.app_ids_names))
    
    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be;
        # find relevant files for parsing
        prefiltered_files = set()
        prefiltered_files.update(self.fileManager.findFiles(dataSource, "%.acf"))
        prefiltered_files.update(self.fileManager.findFiles(dataSource, "%.vdf"))
        self.files = self.__filter_files(prefiltered_files)

        # update the progress bar
        self.update_progress()

        sources = {}
        for file in self.files:

            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            try:
                fname = file.getName()
                fpath = file.getUniquePath()
                fcontent = TSKFileUtils.parse_vdf_file(file, case=self.case)

                if re.match(r"appmanifest_\d+\.acf", fname):
                    # e.g., /deck/.local/share/Steam/steamapps/appmanifest_<ID>.acf
                    d = self.__parse_appmanifest_acf(fcontent)
                elif fname == "registry.vdf" or re.match(r"registry\.vdf\.\d+\.tmp", fname):
                    # e.g., /deck/.steam/registry.vdf
                    d = self.__parse_registry_vdf(fcontent)
                elif fname == "libraryfolders.vdf":
                    # e.g., /deck/.local/share/Steam/config/libraryfolders.vdf
                    #       /deck/.local/share/Steam/steamapps/libraryfolders.vdf
                    d = self.__parse_libraryfolders_vdf(fcontent)
                elif fname == "localconfig.vdf":
                    # e.g., /deck/.local/share/Steam/userdata/<ID>/config/localconfig.vdf
                    d = self.__parse_localconfig_vdf(fcontent)
                else:
                    d = None
                    self.log("Unexpected case: {}".format(file.getUniquePath()))

                if d:
                    sources[fpath] = d
                    self.file_sources[fpath] = file
                
            except Exception as e:
                self.log(msg=file.getUniquePath(), error=e)
            
        # update the progress bar
        self.update_progress()
        
        # get all distinct app IDs found in different sources
        app_ids = set()
        for appdata in sources.values():
            app_ids.update(appdata.keys())
        app_ids = sorted(app_ids, key=int)

        # prepare dictionary template for each found app
        dict_apps = {}
        for app_id in app_ids:
            dict_apps[app_id] = {}
            for attr in self.attributes:
                dict_apps[app_id][attr] = ""

        # merge app information found in different sources
        for app_id, appdata in dict_apps.items():
            for _, sourcedata in sources.items():
                if app_id not in sourcedata:
                    continue
                for k, v in sourcedata[app_id].items():
                    if k in appdata and appdata[k] == "":
                        appdata[k] = v
                    elif k in appdata and appdata[k] != "":
                        assert appdata[k] == v, "{} vs. {}".format(appdata[k], v)
                    elif k not in appdata:
                        appdata[k] = v
        
        # for each given app, add app name if app name was not already found,
        # and if the app name was already found, ensure its consistency 
        # with the app name from the app-ID-to-name dictionary (if app ID exists there).

        for app_id, appdata in dict_apps.items():
            app_name = ""
            if app_id in self.app_ids_names:
                app_name = self.app_ids_names[app_id]
                app_name = app_name.encode('utf-8').decode('ascii', 'ignore')

            if appdata[ArtifactUtils.ATTR_NAME] == "":
                appdata[ArtifactUtils.ATTR_NAME] = app_name

            elif appdata[ArtifactUtils.ATTR_NAME] != "" and app_id in self.app_ids_names:
                if appdata[ArtifactUtils.ATTR_NAME] != self.app_ids_names[app_id]:
                    appdata[ArtifactUtils.ATTR_NAME] = "{} / {}".format(
                        appdata[ArtifactUtils.ATTR_NAME], app_name
                    )

        # create and post artifact on blackboard, if not already existing,
        # using a mockfile to indicate a file object although we evaluated multiple files
        mockfile = self.get_mockup_file_for_multifile_artifacts(dataSource)

        for app_id in sorted(dict_apps.keys(), key=int):
            data = dict(dict_apps[app_id])

            self.make_blackboard_artifact(
                file=mockfile, 
                artifact_data=data)
            
            # update the progress bar
            self.update_progress()

        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK
    
    def __filter_files(self, files):
        filtered_files = set()

        for file in files:
            # skip non-files, slack files, journal files
            if TSKFileUtils.is_non_file(file) \
                or TSKFileUtils.is_slack_file(file) \
                or file.getName().endswith('-journal'):
                continue
            
            # skip non-relevant files
            pattern = r"/deck/(\.local/share/Steam|\.steam)/.*\.(acf|vdf)$"
            if not re.search(pattern, file.getUniquePath()):
                continue
            pattern = r"^(appmanifest_\d+|libraryfolders|localconfig|registry)\.(acf|vdf)$"
            if not re.match(pattern, file.getName()):
                continue

            filtered_files.add(file)

        return filtered_files

    def __parse_localconfig_vdf(self, dict_localconfig):
        assert isinstance(dict_localconfig, OrderedDict) or isinstance(dict_localconfig, dict), \
            "{}: {}".format(type(dict_localconfig), dict_localconfig)
        assert "UserLocalConfigStore" in dict_localconfig, \
            "{} > {}".format(sorted(dict_localconfig.keys()), dict_localconfig)
        data = dict_localconfig["UserLocalConfigStore"]

        apptickets_app_ids = []
        if "apptickets" in data:
            apptickets_app_ids = sorted(map(str, data["apptickets"].keys()))

        nettickets_app_ids = []
        if "nettickets" in data:
            nettickets_app_ids = sorted(map(str, data["nettickets"].keys()))

        for key in ["Software", "Valve", "Steam"]:
            assert key in data, "{}".format(sorted(data.keys()))
            data = data[key]

        software_app_ids = {}
        attributes = [
            "autocloud_lastexit",
            "autocloud_lastlaunch",
            "cloud_last_sync_state",
            "cloud_quota_files",
            "cloud_quota_bytes",
            "cloud_used_files",
            "cloud_used_bytes",
            "lastplayed",
            "playtime",
            "playtime2wks",
        ]
        for app_id, od_v in data["apps"].items():
            assert isinstance(od_v, OrderedDict), "{}".format(type(od_v))
            d_v = TSKFileUtils.flatten_dict(od_v)
            info = {}
            for key in attributes:
                if key in d_v:
                    info[key] = str(d_v[key])
            software_app_ids[app_id] = info

        # sanity check for last playtime
        assert "LastPlayedTimesSyncTime" in data, "{}".format(sorted(data.keys()))
        sanity_check = False
        for app_id, appdata in software_app_ids.items():
            if "lastplayed" in appdata:
                if appdata["lastplayed"] == data["LastPlayedTimesSyncTime"]:
                    sanity_check = True
                    break
            if "autocloud_lastexit" in appdata:
                if appdata["autocloud_lastexit"] == data["LastPlayedTimesSyncTime"]:
                    sanity_check = True
                    break
            if "autocloud_lastlaunch" in appdata:
                if appdata["autocloud_lastlaunch"] == data["LastPlayedTimesSyncTime"]:
                    sanity_check = True
                    break

        # summarize app IDs and app information found in localconfig.vdf
        app_ids = sorted(set(itertools.chain(
            apptickets_app_ids, nettickets_app_ids, software_app_ids.keys()
        )), key=int)

        dict_apps = {}
        for app_id in app_ids:
            dict_apps[app_id] = {'app_id': app_id}
            if app_id in software_app_ids:
                for key in attributes:
                    dict_apps[app_id][key] = software_app_ids[app_id][key] \
                        if key in software_app_ids[app_id] else ""
        
        # convert timestamps to dates
        for app_id, appdata in dict_apps.items():
            for key in ['autocloud_lastexit', 'autocloud_lastlaunch', 'lastplayed']:
                if key in appdata and re.match(r'\d+', appdata[key]):
                    appdata["{}_date".format(key)] = TimestampUtils.epoch_to_date_str(appdata[key])
            
        # rename attributes
        renamings = {
            "app_id": ArtifactUtils.ATTR_APP_ID,
            "lastplayed": ArtifactUtils.ATTR_LASTPLAYED,
            "lastplayed_date": ArtifactUtils.ATTR_LASTPLAYED_DATE,
            "autocloud_lastexit": ArtifactUtils.ATTR_AUTOCLOUD_LASTEXIT,
            "autocloud_lastexit_date": ArtifactUtils.ATTR_AUTOCLOUD_LASTEXIT_DATE,
            "autocloud_lastlaunch": ArtifactUtils.ATTR_AUTOCLOUD_LASTLAUNCH,
            "autocloud_lastlaunch_date": ArtifactUtils.ATTR_AUTOCLOUD_LASTLAUNCH_DATE,
            "cloud_last_sync_state": ArtifactUtils.ATTR_CLOUD_LAST_SYNC_STATE,
            "cloud_quota_files": ArtifactUtils.ATTR_CLOUD_QUOTA_FILES,
            "cloud_quota_bytes": ArtifactUtils.ATTR_CLOUD_QUOTA_BYTES,
            "cloud_used_files": ArtifactUtils.ATTR_CLOUD_USED_FILES,
            "cloud_used_bytes": ArtifactUtils.ATTR_CLOUD_USED_BYTES,
            "playtime": ArtifactUtils.ATTR_PLAYTIME,
            "playtime2wks": ArtifactUtils.ATTR_PLAYTIME_2WKS,
        }

        dict_apps_renamed = {}
        for id_app, appdata in dict_apps.items():
            dict_apps_renamed[id_app] = {}
            for k, v in appdata.items():
                dict_apps_renamed[id_app][renamings[k]] = str(v) if '_date' not in k else v
        
        return dict_apps_renamed

    def __parse_libraryfolders_vdf(self, dict_libraryfolders):
        assert isinstance(dict_libraryfolders, OrderedDict) \
            or isinstance(dict_libraryfolders, dict), \
            "{}: {}".format(dict_libraryfolders(data), dict_libraryfolders)
        
        if "libraryfolders" in dict_libraryfolders:
            data = dict_libraryfolders["libraryfolders"]
        elif "LibraryFolders" in dict_libraryfolders:
            data = dict_libraryfolders["LibraryFolders"]
        else:
            data = None

        assert isinstance(data, OrderedDict) or isinstance(data, dict), \
            "{}: {} << {}".format(type(data), data, dict_libraryfolders)

        dict_apps = {}
        for _, od_appinfo in data.items():
            assert isinstance(od_appinfo, OrderedDict) or isinstance(od_appinfo, dict), \
                "{}: {}".format(type(od_appinfo), od_appinfo)
            appinfo = dict(od_appinfo)

            if "apps" in appinfo:
                assert isinstance(appinfo["apps"], OrderedDict) \
                    or isinstance(appinfo["apps"], dict), \
                    "{}: {}".format(type(appinfo["apps"]), od_appinfo["apps"])
                for app_id, _ in appinfo["apps"].items():
                    dict_apps[app_id] = { ArtifactUtils.ATTR_APP_ID: str(app_id) }
        
        return dict_apps

    def lowercase_keys(self,obj):
        if isinstance(obj, dict):
            obj={key.lower():value for key, value in obj.items()}
            for key, value in obj.items():
                if isinstance(value, list):
                    for idx, item in enumerate(value):
                        value[idx]=self.lowercase_keys(item)
                obj[key]=self.lowercase_keys(value)
        return obj

    def __parse_appmanifest_acf(self, dict_appmanifest):
        lc_dict=self.lowercase_keys(dict_appmanifest)
        assert isinstance(dict_appmanifest, OrderedDict) or isinstance(dict_appmanifest, dict), \
            "{}".format(type(dict_appmanifest))
        assert "appstate" in lc_dict, "{}".format(json.dumps(dict_appmanifest))
        assert "lastowner" in lc_dict["appstate"], "{}".format(json.dumps(dict_appmanifest))
        assert "lastupdated" in lc_dict["appstate"], "{}".format(json.dumps(dict_appmanifest))
        assert "appid" in lc_dict["appstate"], "{}".format(json.dumps(dict_appmanifest))
        assert "name" in lc_dict["appstate"], "{}".format(json.dumps(dict_appmanifest))

        dict_app = {}
        dict_app[str(lc_dict["appstate"]["appid"])] = {
            ArtifactUtils.ATTR_NAME: str(lc_dict["appstate"]["name"]),
            ArtifactUtils.ATTR_APP_ID: str(lc_dict["appstate"]["appid"]),
            ArtifactUtils.ATTR_OWNER_STEAM_ID: \
                str(lc_dict["appstate"]["lastowner"]),
            ArtifactUtils.ATTR_LASTUPDATED: \
                str(lc_dict["appstate"]["lastupdated"]),
            ArtifactUtils.ATTR_LASTUPDATED_DATE: \
                TimestampUtils.epoch_to_date_str(lc_dict["appstate"]["lastupdated"]),
        }
        
        return dict_app

    def __parse_registry_vdf(self, dict_registry):
        dict_apps = {}

        try:
            assert isinstance(dict_registry, OrderedDict) or isinstance(dict_registry, dict), \
                "{}".format(type(dict_registry))
            data = dict(dict_registry)

            for key in ["Registry", "HKCU", "Software", "Valve", "Steam"]:
                assert key in data, "{} > {}".format(key, sorted(data[key].keys()))
                data = data[key]
        except Exception as e:
            self.log(msg=data, error=e)
            return dict_apps
        
        if "apps" in data:
            for app_id, info in data["apps"].items():

                try:
                    if "Installed" in info:
                        assert info["Installed"] in ["0", "1"], "{}".format(info["Installed"])  
                    if "Running" in info:
                        assert info["Running"] in ["0", "1"], "{}".format(info["Running"])
                    if "Updating" in info:
                        assert info["Updating"] in ["0", "1"], "{}".format(info["Updating"])
                except Exception as e:
                    self.log(msg=data, error=e)
                    continue
                
                app = {
                    ArtifactUtils.ATTR_APP_ID: str(app_id),
                    ArtifactUtils.ATTR_NAME: info["name"] if "name" in info else "",
                    ArtifactUtils.ATTR_AUTO_LOGIN_USER: str(data["AutoLoginUser"]) if "AutoLoginUser" in data else "",
                    ArtifactUtils.ATTR_INSTALLED: str(info["Installed"] == "1") \
                        if "Installed" in info else "",
                    ArtifactUtils.ATTR_RUNNING: str(info["Running"] == "1") \
                        if "Running" in info else "",
                    ArtifactUtils.ATTR_UPDATING: str(info["Updating"] == "1") \
                        if "Updating" in info else "",
                }

                dict_apps[str(app_id)] = app

        return dict_apps
