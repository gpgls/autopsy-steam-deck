# -*- coding: utf-8 -*-

import os
import re
import sys
from java.sql import SQLException
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.autopsyplus import FileIngestModulePlus
from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils
from utils.timestamp import TimestampUtils
from utils.module import VERSION, MODULE_WEB_QUOTAMANAGER


class SteamDeckWebQuotaManagerFIMFactory(IngestModuleFactoryAdapter):

    moduleName = "{}".format(MODULE_WEB_QUOTAMANAGER)

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Extracting QuotaManager database from disk images of Steam Deck devices."

    def getModuleVersionNumber(self):
        return "{}".format(VERSION)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, _):
        return SteamDeckWebQuotaManagerFIM()


class SteamDeckWebQuotaManagerFIM(FileIngestModulePlus):

    def __init__(self):
        FileIngestModulePlus.__init__(
            self,
            SteamDeckWebQuotaManagerFIMFactory.moduleName,
            [
                ArtifactUtils.ATTR_WEB_QUOTAMANAGER_ORIGIN,
                ArtifactUtils.ATTR_WEB_QUOTAMANAGER_TYPE,
                ArtifactUtils.ATTR_WEB_QUOTAMANAGER_USED_COUNT,
                ArtifactUtils.ATTR_WEB_QUOTAMANAGER_LAST_ACCESS_UTC,
                ArtifactUtils.ATTR_WEB_QUOTAMANAGER_LAST_MODIFIED_UTC,
            ]
        )

    def process(self, file):
        # skip non-files and slack files
        if TSKFileUtils.is_non_file(file) or TSKFileUtils.is_slack_file(file):
            return IngestModule.ProcessResult.OK
        
        # process files that are of interest
        try:
            data = self.__process(file)
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
            return IngestModule.ProcessResult.ERROR

        # create and post artifact(s) on blackboard, if not already existing
        for d in data:
            self.make_blackboard_artifact(file, d)

        return IngestModule.ProcessResult.OK
    
    def __process(self, file):
        data = []
        fpath = file.getUniquePath()

        if re.search(r'deck\/\.local\/share\/Steam\/config\/htmlcache\/QuotaManager$', fpath):
            data.extend(self.__parse_cookies_db(file))
        
        return data

    def __parse_cookies_db(self, file):
        data = []

        fh = None
        dbConn = None
        stmt = None

        try:
            dbConn, fh = TSKFileUtils.open_sqlite_file(file, case=self.case)
        except SQLException as e:
            self.log(msg=file.getUniquePath(), error=e)

        if dbConn:

            dict_cols_mapping = {
                'origin': ArtifactUtils.ATTR_WEB_QUOTAMANAGER_ORIGIN,
                'type': ArtifactUtils.ATTR_WEB_QUOTAMANAGER_TYPE,
                'used_count': ArtifactUtils.ATTR_WEB_QUOTAMANAGER_USED_COUNT,
                'last_access_time': ArtifactUtils.ATTR_WEB_QUOTAMANAGER_LAST_ACCESS_UTC,
                'last_modified_time': ArtifactUtils.ATTR_WEB_QUOTAMANAGER_LAST_MODIFIED_UTC,
            }

            try:
                stmt = dbConn.createStatement()
                results = stmt.executeQuery("SELECT * FROM OriginInfoTable;")
                while results.next():
                    d = self.get_data_template()

                    for col, key in dict_cols_mapping.items():
                        try:
                            if col in ["last_access_time", "last_modified_time"]:
                                d[key] = TimestampUtils.webkit_to_date_str(
                                    results.getString(col))
                            else:
                                d[key] = results.getString(col)
                        except Exception as e:
                            d[key] = ArtifactUtils.ERR_PARSE
                            self.log("{} >> col={} >> key={} >> {} >> {}".format(
                                file.getUniquePath(), col, key, e.__class__.__name__, e.message))

                    data.append(d)

            except SQLException as e:
                self.log(msg=file.getUniquePath(), error=e)

        TSKFileUtils.close_sqlite_file(dbConn, fh)

        return data
