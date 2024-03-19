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
from utils.module import VERSION, MODULE_LOG_ENTRIES


class SteamDeckLogEntriesDSIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_LOG_ENTRIES)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "VERY SLOW. TAKES HOURS. Extracting Steam log file entries from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, _):
        return SteamDeckLogEntriesDSIM()


class SteamDeckLogEntriesDSIM(DataSourceIngestModulePlus):

    def __init__(self):
        DataSourceIngestModulePlus.__init__(
            self,
            SteamDeckLogEntriesDSIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_LOG_TIMESTAMP,
                ArtifactUtils.ATTR_LOG_MESSAGE,
                ArtifactUtils.ATTR_FILE_PATH,
            ]
        )

    def process(self, dataSource, progressBar):
        DataSourceIngestModulePlus.process(self, dataSource, progressBar)

        # determine how much work there will be by pre-filtering files
        self.files = [file for file in self.fileManager.findFiles(dataSource, "%.txt") \
                 if 'deck/.local/share/Steam/logs/' in file.getUniquePath()]
        
        # update the progress bar
        self.update_progress()

        # parse log entries from files
        data = []
        rel_index = 1

        for file in self.files:
            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK

            try:
                d, rel_index = self.__process(file, rel_index)
                if d:
                    data.extend(d)
                    for item in d:
                        if list(item)[2] not in self.file_sources:
                            self.file_sources[list(item)[2]] = file

            except Exception as e:
                self.log(msg=file.getUniquePath(), error=e)

        # update the progress bar
        self.update_progress()
       
        # sort log entries
        for d_tuple in sorted(data, key=lambda x: (x[0], x[2], x[3])):

            if self.is_job_cancelled():
                return IngestModule.ProcessResult.OK
            
            # create data object
            d = self.get_data_template()
            d[ArtifactUtils.ATTR_LOG_TIMESTAMP] = list(d_tuple)[0]
            d[ArtifactUtils.ATTR_LOG_MESSAGE] = list(d_tuple)[1]
            d[ArtifactUtils.ATTR_FILE_PATH] = list(d_tuple)[2]
            
            # create and post artifact on blackboard
            self.make_blackboard_artifact(
                self.file_sources[d[ArtifactUtils.ATTR_FILE_PATH]], d, skip_fileinfo=True)
            
            # update the progress bar
            self.update_progress()

        # finish
        self.shutDown()
        return IngestModule.ProcessResult.OK

    def __process(self, file, rel_index):
        data = []

        # open log file
        fh = None
        try:
            fh = TSKFileUtils.open_file(file, case=self.case)
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
            TSKFileUtils.close_file(fh)
            return data

        # parse log file
        if file.getName() in [
            "appinfo_log.txt",
            "bluetoothmanager.txt",
            "bootstrap_log.txt",
            "client_networkmanager.txt",
            "cloud_log.txt",
            "compat_log.txt",
            "configstore_log.txt",
            "connection_log.txt",
            "content_log.txt",
            "durationcontrol_log.txt",
            "librarysharing_log.txt",
            "parental_log.txt",
            "remote_connections.txt",
            "shader_log.txt",
            "sitelicense_log.txt",
            "stats_log.txt",
            "steamui_audio.txt",
            "steamui_html.txt",
            "steamui_system.previous.txt",
            "steamui_system.txt",
            "steamui_update.txt",
            "streaming_log.txt",
            "systemaudiomanager.txt",
            "systemdisplaymanager.txt",
            "systemdockmanager.txt",
            "systemmanager.txt",
            "systemperfmanager.txt",
            "text_filter_log.txt",
            "timedtrial_log.txt",
            "transport_steamui.txt",
            "webhelper.txt",
            "workshop_log.txt"
        ]:
            d, rel_index = self.__parse_log_txt(file, fh, rel_index, enable_prev_ts=False)
            data.extend(d)

        elif file.getName() in ["controller.txt", "controller_ui.txt", "console_log.txt"]:
            d, rel_index = self.__parse_log_txt(file, fh, rel_index, enable_prev_ts=True)
            data.extend(d)

        # close log file
        TSKFileUtils.close_file(fh)
        
        return data, rel_index

    def __parse_log_txt(self, file, fh, rel_index, enable_prev_ts = False):
        data = []

        pattern = r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+(.*)$"
        pattern_ts = r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]"
        prev_ts = None

        for line in fh.readlines():
            l = line.strip()
            if not l:
                continue
            
            if not enable_prev_ts:
                m = re.match(pattern, l)
                if m:
                    t = (m.groups()[0].strip(), m.groups()[1].strip(), 
                            file.getUniquePath(), rel_index)
                    data.append(t)
                    rel_index += 1

            else:
                m = re.search(pattern_ts, l)
                if m:
                    prev_ts = m.groups()[0].strip()
                    m = re.match(pattern, l)
                    if m:
                        t = (m.groups()[0].strip(), m.groups()[1].strip(), 
                                file.getUniquePath(), rel_index)
                        data.append(t)
                        rel_index += 1
                else:
                    t = (prev_ts, l, file.getUniquePath(), rel_index)
                    data.append(t)
                    rel_index += 1

        return data, rel_index
