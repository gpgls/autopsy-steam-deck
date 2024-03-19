# -*- coding: utf-8 -*-

import os
import re
import sys
import string
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import DataSourceIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.timestamp import TimestampUtils
from utils.module import VERSION, MODULE_DEVICE


class SteamDeckDeviceDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_DEVICE)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting device information from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckDeviceDSIM()


class SteamDeckDeviceDSIM(DataSourceIngestModulePlus):

    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self,
            SteamDeckDeviceDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_DEVICE_KEY,
                ArtifactUtils.ATTR_DEVICE_VALUE,
                ArtifactUtils.ATTR_FILE_PATH
            ]
        )

    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be by pre-filtering files/directories
        self.files = self.fileManager.findFiles(dataSource, "%")
        
        # update the progress bar
        self.update_progress()

        for file in self.files:
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            fname = file.getName()
            fpath = file.getUniquePath()

            # kernel
            if 'linux' in fname \
                and 'valve' in fname \
                and '/lib/pacman/local/' in fpath \
                and '/usr/share/factory/' not in fpath:

                self.make_blackboard_artifact(file=file, artifact_data={
                    ArtifactUtils.ATTR_DEVICE_KEY: "Kernel Version",
                    ArtifactUtils.ATTR_DEVICE_VALUE: fname,
                    ArtifactUtils.ATTR_FILE_PATH: fpath,
                })

                self.update_progress()
                continue
        
            # skip non-files and slack files
            if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
               self.update_progress()
               continue
            
            # extract information from relevant files
            fh = None

            if fname == "steamcl-version":
                try:
                    fh = TSKFileUtils.open_file(file)
                    matches = re.findall(r'([a-f0-9]{64})\s+(.*)', fh.read())
                    if matches:
                        for m in matches:
                            sha256 = list(m)[0].strip()
                            version = list(m)[1].strip()
                
                    
                    self.make_blackboard_artifact(file=file, artifact_data={
                        ArtifactUtils.ATTR_DEVICE_KEY: "Steam Client Version",
                        ArtifactUtils.ATTR_DEVICE_VALUE: version,
                        ArtifactUtils.ATTR_FILE_PATH: fpath,
                    })
                    self.make_blackboard_artifact(file=file, artifact_data={
                        ArtifactUtils.ATTR_DEVICE_KEY: "Steam Client Version (SHA256)",
                        ArtifactUtils.ATTR_DEVICE_VALUE: sha256,
                        ArtifactUtils.ATTR_FILE_PATH: fpath,
                    })
                except Exception as e:
                    self.log(msg=fpath, error=e)
            
            if fname == "NetworkManager.state":
                try:
                    config = TSKFileUtils.parse_config_file(file, lowercase=False)
                    for key, value in config.items():
                        k = re.sub(r"^main_", "", key, flags=re.I).strip()
                        self.make_blackboard_artifact(file=file, artifact_data={
                            ArtifactUtils.ATTR_DEVICE_KEY: k,
                            ArtifactUtils.ATTR_DEVICE_VALUE: value,
                            ArtifactUtils.ATTR_FILE_PATH: fpath,
                        })
                except Exception as e:
                    self.log(msg=fpath, error=e)

            if fname in ["lsb-release", ".devkit-service-on-os-update"]:
                try:
                    fh = TSKFileUtils.open_file(file)
                    for line in fh.readlines():
                        l = line.strip()
                        if not l:
                            continue
                        key, value = l.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        self.make_blackboard_artifact(file=file, artifact_data={
                            ArtifactUtils.ATTR_DEVICE_KEY: key,
                            ArtifactUtils.ATTR_DEVICE_VALUE: value,
                            ArtifactUtils.ATTR_FILE_PATH: fpath,
                        })
                except Exception as e:
                    self.log(msg=fpath, error=e)
            
            if fname == "ktimezonedrc":
                try:
                    config = TSKFileUtils.parse_config_file(file, lowercase=False)
                    for key, value in config.items():
                        k = re.sub(r"^TimeZones_", "", key, flags=re.I).strip()
                        if k.lower() in ["localzone"]:
                            self.make_blackboard_artifact(file=file, artifact_data={
                                ArtifactUtils.ATTR_DEVICE_KEY: k,
                                ArtifactUtils.ATTR_DEVICE_VALUE: value,
                                ArtifactUtils.ATTR_FILE_PATH: fpath,
                            })
                except Exception as e:
                    self.log(msg=fpath, error=e)
            
            if fname.startswith("internal-") and fname.endswith(".lease"):
                try:
                    fh = TSKFileUtils.open_file(file)
                    for line in fh.readlines():
                        l = line.strip()
                        if not l or l.startswith('#'):
                            continue
                        key, value = l.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        self.make_blackboard_artifact(file=file, artifact_data={
                            ArtifactUtils.ATTR_DEVICE_KEY: key,
                            ArtifactUtils.ATTR_DEVICE_VALUE: value,
                            ArtifactUtils.ATTR_FILE_PATH: fpath,
                        })

                except Exception as e:
                    self.log(msg=fpath, error=e)

            if fname == 'user-dirs.locale':
                try:
                    fh = TSKFileUtils.open_file(file)
                    value = str(fh.read())
                    self.make_blackboard_artifact(file=file, artifact_data={
                        ArtifactUtils.ATTR_DEVICE_KEY: "User Directory Locale",
                        ArtifactUtils.ATTR_DEVICE_VALUE: value,
                        ArtifactUtils.ATTR_FILE_PATH: fpath,
                    })

                except Exception as e:
                    self.log(msg=fpath, error=e)
            
            if '/lib/overlays/etc/upper/machine-id' in fpath:
                try:
                    fh = TSKFileUtils.open_file(file)
                    value = str(fh.read())
                    self.make_blackboard_artifact(file=file, artifact_data={
                        ArtifactUtils.ATTR_DEVICE_KEY: "Machine ID",
                        ArtifactUtils.ATTR_DEVICE_VALUE: value,
                        ArtifactUtils.ATTR_FILE_PATH: fpath,
                    })

                except Exception as e:
                    self.log(msg=fpath, error=e)
            
            if '-biosupdate/last_auto_attempt' in fpath:
                try:
                    fh = TSKFileUtils.open_file(file)
                    value = TimestampUtils.epoch_to_date_str(str(fh.read()))
                    self.make_blackboard_artifact(file=file, artifact_data={
                        ArtifactUtils.ATTR_DEVICE_KEY: "Last Auto Attempt BIOS Update",
                        ArtifactUtils.ATTR_DEVICE_VALUE: value,
                        ArtifactUtils.ATTR_FILE_PATH: fpath,
                    })

                except Exception as e:
                    self.log(msg=fpath, error=e)

            if fname == 'steam_client_steamdeck_stable_ubuntu12.manifest':
                try:
                    data = TSKFileUtils.parse_vdf_file(file=file, case=self.case)
                    if 'ubuntu12' in data and 'version' in data['ubuntu12']:
                        self.make_blackboard_artifact(file=file, artifact_data={
                            ArtifactUtils.ATTR_DEVICE_KEY: "Steam Client Version",
                            ArtifactUtils.ATTR_DEVICE_VALUE: str(data['ubuntu12']['version']),
                            ArtifactUtils.ATTR_FILE_PATH: fpath,
                        })
                        self.make_blackboard_artifact(file=file, artifact_data={
                            ArtifactUtils.ATTR_DEVICE_KEY: "Steam Client Version (Parsed)",
                            ArtifactUtils.ATTR_DEVICE_VALUE: \
                                TimestampUtils.epoch_to_date_str(data['ubuntu12']['version']),
                            ArtifactUtils.ATTR_FILE_PATH: fpath,
                        })

                except Exception as e:
                    self.log(msg=fpath, error=e)

            # clean up, and update the progress bar
            TSKFileUtils.close_file(fh)
            self.update_progress()

        # update the progress bar
        self.update_progress()
        
        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK
