# -*- coding: utf-8 -*-

import os
import sys
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_LOG_FILES


class SteamDeckLogFilesFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_LOG_FILES)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting Steam Deck log files from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckLogFilesFIM()


class SteamDeckLogFilesFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckLogFilesFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_FILE_NAME,
                ArtifactUtils.ATTR_FILE_PATH
            ]
        )

    def process(self, file):
        # skip non-files and slack files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # skip files that are not of interest
        if 'deck/.local/share/Steam/logs/' not in file.getUniquePath():
            return IngestModule.ProcessResult.OK

        data = {
            ArtifactUtils.ATTR_FILE_NAME: file.getName(),
            ArtifactUtils.ATTR_FILE_PATH: file.getUniquePath()
        }

        # create and post artifact(s) on blackboard, if not already existing
        self.make_blackboard_artifact(file, data)

        return IngestModule.ProcessResult.OK
