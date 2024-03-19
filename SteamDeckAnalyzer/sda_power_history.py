# -*- coding: utf-8 -*-

import os
import re
import sys
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import DataSourceIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.timestamp import TimestampUtils
from utils.module import VERSION, MODULE_POWER_HISTORY


class SteamDeckPowerHistoryDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_POWER_HISTORY)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting power history from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckPowerHistoryDSIM()


class SteamDeckPowerHistoryDSIM(DataSourceIngestModulePlus):

    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self,
            SteamDeckPowerHistoryDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_POWERHISTORY_TIMESTAMP,
                ArtifactUtils.ATTR_POWERHISTORY_TYPE,
                ArtifactUtils.ATTR_POWERHISTORY_VALUE,
                ArtifactUtils.ATTR_POWERHISTORY_STATUS,
            ]
        )
    
    def startUp(self, context):
        DataSourceIngestModulePlus.startUp(self, context)

    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be by pre-filtering files
        self.files = self.fileManager.findFiles(dataSource, "history-%")

        # update the progress bar
        self.update_progress()

        items = []
        for file in self.files:
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK
            
            # skip non-files
            if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
                continue
            # skip non-relevant files
            if '/lib/upower/history-' not in file.getUniquePath():
                continue
            if not file.getName().endswith('.dat'):
                continue

            # parse contents of relevant file
            items.extend(self.__process(file))

        # update the progress bar
        self.update_progress()

        # create and post sorted artifacts on blackboard, if not already existing
        for d_tuple in sorted(items, key=lambda x: x[0]):
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK
            
            d_list = list(d_tuple)
            self.make_blackboard_artifact(file=d_list[4], artifact_data={
                ArtifactUtils.ATTR_POWERHISTORY_TIMESTAMP: \
                    TimestampUtils.epoch_to_date_str(d_list[0]),
                ArtifactUtils.ATTR_POWERHISTORY_TYPE: d_list[1],
                ArtifactUtils.ATTR_POWERHISTORY_VALUE: d_list[2],
                ArtifactUtils.ATTR_POWERHISTORY_STATUS: d_list[3],
            })
            self.update_progress()

        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK

    def __process(self, file):
        fh = None
        items = []

        try:
            type_ = " ".join(map(str.title, str(file.getName()).split('-')[0:2]))
            fh = TSKFileUtils.open_file(file=file, case=self.case)

            for line in fh.readlines():
                l = line.strip()
                if not l:
                    continue

                m = re.match(r"(\d+)\s+([^\s]*)\s+(.*)", l)
                if not m:
                    continue

                items.append((
                    m.groups()[0],  # timestamp
                    type_,
                    str(m.groups()[1]),  # value
                    str(m.groups()[2]),  # status
                    file
                ))
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
        
        TSKFileUtils.close_file(fh)
        return items