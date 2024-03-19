# -*- coding: utf-8 -*-

import os
import sys
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_BOOT_PARTITIONS


class SteamDeckPartitionsFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_BOOT_PARTITIONS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting boot partition information from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckPartitionsFIM()


class SteamDeckPartitionsFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckPartitionsFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_BOOT_ATTEMPTS,
                ArtifactUtils.ATTR_BOOT_COUNT,
                ArtifactUtils.ATTR_BOOT_OTHER,
                ArtifactUtils.ATTR_BOOT_OTHER_DISABLED,
                ArtifactUtils.ATTR_BOOT_REQUESTED_AT,
                ArtifactUtils.ATTR_BOOT_TIME,
                ArtifactUtils.ATTR_BOOT_COMMENT,
                ArtifactUtils.ATTR_BOOT_IMAGE_INVALID,
                ArtifactUtils.ATTR_BOOT_LOADER,
                ArtifactUtils.ATTR_BOOT_PARTITIONS,
                ArtifactUtils.ATTR_BOOT_TITLE,
                ArtifactUtils.ATTR_BOOT_UPDATE,
                ArtifactUtils.ATTR_BOOT_UPDATE_DISABLED,
                ArtifactUtils.ATTR_BOOT_UPDATE_WINDOW_END,
                ArtifactUtils.ATTR_BOOT_UPDATE_WINDOW_START,
            ]
        )

    def process(self, file):
        # skip non-files and slack files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # skip files that are not of interest
        if "SteamOS/conf/" not in file.getUniquePath():
            return IngestModule.ProcessResult.OK
        if file.getName() not in ["A.conf", "B.conf"]:
            return IngestModule.ProcessResult.OK
        
        # extract information from `A.conf` or `B.conf`
        data = self.parse_boot_config(TSKFileUtils.parse_boot_config(file))

        # create and post artifact on blackboard, if not already existing
        self.make_blackboard_artifact(file, data)

        return IngestModule.ProcessResult.OK

    def parse_boot_config(self, dict_boot_config):
        assert isinstance(dict_boot_config, dict), \
            "{}: {}".format(type(dict_boot_config), dict_boot_config)

        renamings = {
            'boot-attempts': ArtifactUtils.ATTR_BOOT_ATTEMPTS,
            'boot-count': ArtifactUtils.ATTR_BOOT_COUNT,
            'boot-other': ArtifactUtils.ATTR_BOOT_OTHER,
            'boot-other-disabled': ArtifactUtils.ATTR_BOOT_OTHER_DISABLED,
            'boot-requested-at': ArtifactUtils.ATTR_BOOT_REQUESTED_AT,
            'boot-time': ArtifactUtils.ATTR_BOOT_TIME,
            'comment': ArtifactUtils.ATTR_BOOT_COMMENT,
            'image-invalid': ArtifactUtils.ATTR_BOOT_IMAGE_INVALID,
            'loader': ArtifactUtils.ATTR_BOOT_LOADER,
            'partitions': ArtifactUtils.ATTR_BOOT_PARTITIONS,
            'title': ArtifactUtils.ATTR_BOOT_TITLE,
            'update': ArtifactUtils.ATTR_BOOT_UPDATE,
            'update-disabled': ArtifactUtils.ATTR_BOOT_UPDATE_DISABLED,
            'update-window-end': ArtifactUtils.ATTR_BOOT_UPDATE_WINDOW_END,
            'update-window-start': ArtifactUtils.ATTR_BOOT_UPDATE_WINDOW_START,
        }

        data = {}
        for k, v in dict_boot_config.items():
            if k in renamings:
                data[renamings[k]] = str(v)

        return data
