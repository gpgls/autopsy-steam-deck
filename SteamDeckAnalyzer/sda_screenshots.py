# -*- coding: utf-8 -*-

import os
import re
import sys
from datetime import datetime
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_SCREENSHOTS


class SteamDeckScreenshotsFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_SCREENSHOTS)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting screenshots from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckScreenshotsFIM()


class SteamDeckScreenshotsFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckScreenshotsFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_APP_ID,
                ArtifactUtils.ATTR_FRIEND_ID,
                ArtifactUtils.ATTR_TIMESTAMP,
                #
                ArtifactUtils.ATTR_FILE_SIZE,
                ArtifactUtils.ATTR_FILE_TYPE,
                ArtifactUtils.ATTR_FILE_TYPE_MIME
            ]
        )

    def process(self, file):
         # skip non-files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK

        # skip files that are not of interest
        pattern = r"/deck/.local/share/Steam/userdata/(\d+)/760/remote/(\d+)/screenshots/(\d{14}_\d+)\.(jpe?g|png|gif)"
        match = re.search(pattern, file.getUniquePath())
        if not match:
            return IngestModule.ProcessResult.OK

        data = {}

        try:
            # parse contents from file path
            data[ArtifactUtils.ATTR_FRIEND_ID] = str(match.groups()[0])
            data[ArtifactUtils.ATTR_APP_ID] = str(match.groups()[1])
            data[ArtifactUtils.ATTR_TIMESTAMP] = \
                datetime.strptime(file.getName().split("_", 1)[0], '%Y%m%d%H%M%S')\
                    .strftime('%Y-%m-%d %H:%M:%S')

            # create and post artifact on blackboard, if not already existing
            self.make_blackboard_artifact(file, data)
        
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
            return IngestModule.ProcessResult.ERROR

        return IngestModule.ProcessResult.OK
