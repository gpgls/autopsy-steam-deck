# -*- coding: utf-8 -*-

import os
import sys
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import DataSourceIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.module import VERSION, MODULE_FACTORY_RESET


class SteamDeckFactoryResetDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_FACTORY_RESET)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Detecting a factory reset in disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckFactoryResetDSIM()


class SteamDeckFactoryResetDSIM(DataSourceIngestModulePlus):

    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self,
            SteamDeckFactoryResetDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_DETECTED,
                ArtifactUtils.ATTR_INTERPRETATION,
                ArtifactUtils.ATTR_DATE_CR,
                ArtifactUtils.ATTR_DATE_M,
                ArtifactUtils.ATTR_DATE_A,
                ArtifactUtils.ATTR_DATE_C,
                ArtifactUtils.ATTR_FILE_PATH,
            ]
        )

    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be by pre-filtering files/directories
        self.files = self.fileManager.findFiles(dataSource, "%factory-res%")
        
        # update the progress bar
        self.update_progress()

        found = False
        for file in self.files:
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            # ignore files as well as non-relevant directories
            skip = False 
            if file.isFile():
                skip = True
            if 'efi/steamos/factory-reset' not in file.getUniquePath():
                skip = True

            if not skip:
                found = True
                fileinfo = TSKFileUtils.get_file_info(file)
                
                # create and post artifact on blackboard, if not already existing
                self.make_blackboard_artifact(file=file, artifact_data={
                    ArtifactUtils.ATTR_INTERPRETATION: \
                        "Existence of directory `efi/steamos/factory-reset` may indicate that a factory reset occurred",
                    ArtifactUtils.ATTR_DETECTED: str(True),
                    ArtifactUtils.ATTR_DATE_CR: fileinfo[ArtifactUtils.ATTR_DATE_CR],
                    ArtifactUtils.ATTR_DATE_M: fileinfo[ArtifactUtils.ATTR_DATE_M],
                    ArtifactUtils.ATTR_DATE_A: fileinfo[ArtifactUtils.ATTR_DATE_A],
                    ArtifactUtils.ATTR_DATE_C: fileinfo[ArtifactUtils.ATTR_DATE_C],
                    ArtifactUtils.ATTR_FILE_PATH: file.getUniquePath(),
                })
            
            # update the progress bar
            self.update_progress()

        if not found:
            # create and post mock artifact on blackboard 
            # so the artifact category for this module will be displayed
            mockfile = self.get_mockup_file_for_multifile_artifacts(dataSource)

            self.make_blackboard_artifact(
                file=mockfile, 
                artifact_data={
                    ArtifactUtils.ATTR_INTERPRETATION: \
                        "Non-existence of directory `efi/steamos/factory-reset` may indicate that a factory reset has not occurred (yet)",
                    ArtifactUtils.ATTR_DETECTED: str(False),
                    ArtifactUtils.ATTR_DATE_CR: "-",
                    ArtifactUtils.ATTR_DATE_M: "-",
                    ArtifactUtils.ATTR_DATE_A: "-",
                    ArtifactUtils.ATTR_DATE_C: "-",
                    ArtifactUtils.ATTR_FILE_PATH: mockfile.getUniquePath(),
                }
            )

        # update the progress bar
        self.update_progress()
        
        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK
