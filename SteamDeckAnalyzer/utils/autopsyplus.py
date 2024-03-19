# -*- coding: utf-8 -*-

import inspect
import traceback
from collections import OrderedDict
from java.util import ArrayList
from java.util.logging import Level
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException

from utils.artifact import ArtifactUtils
from utils.tsk_file import TSKFileUtils


class IngestModulePlus(object):
    def __init__(self, moduleName, attributes):
        self.moduleName = moduleName
        self.artifact_type_label = ArtifactUtils.get_module_artifact_label(self.moduleName)

        self.attributes = attributes
        for attr in [ArtifactUtils.ATTR_FILE_PATH, ArtifactUtils.ATTR_DUPLICATE_CHECK_ID]:
            if attr not in self.attributes:
                self.attributes.append(attr)

        self.context = None
        self.case = None
        self.skCase = None
        self.blackboard = None
        self.artifact_type = None

        self._logger = Logger.getLogger(self.moduleName)

    def startUp(self, context):
        self.context = context
        self.case = Case.getCurrentCase()
        self.skCase = self.case.getSleuthkitCase()
        self.blackboard = self.skCase.getBlackboard()

        # create artifact type
        self.artifact_type = self.blackboard.getOrAddArtifactType(
            self.artifact_type_label, self.moduleName)

        # create artifact attributes and set corresponding member variables
        for key_attr in self.attributes:
            self.blackboard.getOrAddAttributeType(key_attr, 
                                       ArtifactUtils.get_attribute_type(key_attr),
                                       ArtifactUtils.get_attribute_label(key_attr))

    def shutDown(self):
        pass

    def is_job_cancelled(self):
        # check if the user pressed cancel while we were busy
        return self.context.isJobCancelled()

    def get_data_template(self):
        data = OrderedDict()
        for attribute in self.attributes:
            data[attribute] = ""
        return data
    
    def make_blackboard_artifact(self, file, artifact_data, skip_fileinfo=False):
        if not artifact_data:
            return

        # create data object
        data = self.__create_data_object(file, artifact_data, skip_fileinfo)
        if not data:
            return

        # check whether data object already exists in blackboard, and skip if it already exists
        artifact_type_id = self.artifact_type.getTypeID()
        if self.__is_data_object_duplicate(artifact_type_id, data):
            return

        # create new artifact object, and post new artifact on blackboard
        artifact = self.__create_artifact_object(artifact_type_id, data, file)
        if artifact:
            self.blackboard.postArtifact(artifact, self.moduleName, self.context.getJobId())

    def __create_data_object(self, file, artifact_data, skip_fileinfo=False):
        try:
            # merge artifact data with file information of artifact file
            data = self.get_data_template()
            data.update(artifact_data)

            if not skip_fileinfo:
                for k, v in TSKFileUtils.get_file_info(file).items():
                    if k not in data or (data[k] == "" and v != ""):
                        data.update({k: v})
            
            # create duplicate check ID
            data[ArtifactUtils.ATTR_DUPLICATE_CHECK_ID] = \
                TSKFileUtils.create_duplicate_check_id(data, self.attributes)

            return data
        
        except Exception as e:
            self.log(msg=file.getUniquePath(), error=e)
            return None
    
    def __is_data_object_duplicate(self, artifact_type_id, data):
        try:
            for artifact in self.skCase.getBlackboardArtifacts(artifact_type_id):
                attr_type = self.blackboard.getOrAddAttributeType(
                    ArtifactUtils.ATTR_DUPLICATE_CHECK_ID, 
                    ArtifactUtils.get_attribute_type(ArtifactUtils.ATTR_DUPLICATE_CHECK_ID),
                    ArtifactUtils.get_attribute_label(ArtifactUtils.ATTR_DUPLICATE_CHECK_ID))
                attr = artifact.getAttribute(attr_type)
                if attr and attr.getValueString() == data[ArtifactUtils.ATTR_DUPLICATE_CHECK_ID]:
                    return True
            return False
        
        except Exception as e:
            self.log(msg=artifact_type_id, error=e)
            return True
    
    def __create_artifact_object(self, artifact_type_id, data, file):
        try:
            artifact = file.newArtifact(artifact_type_id)
            
            attrs = ArrayList()
            for key_attr in self.attributes:
                if key_attr in data:
                    attr = self.blackboard.getOrAddAttributeType(key_attr, 
                        ArtifactUtils.get_attribute_type(key_attr),
                        ArtifactUtils.get_attribute_label(key_attr))
                    attrs.add(BlackboardAttribute(attr, self.moduleName, data[key_attr]))
            
            artifact.addAttributes(attrs)

            return artifact
        
        except Exception as e:
            self.log(msg=artifact_type_id, error=e)
            return None

    def log(self, msg, error=None):
        name =  self.__class__.__name__
        stack = inspect.stack()[1][3]
        message = "[{}] {}".format(self.moduleName, msg)
        if error:
            message = "{} >> {} >> {} >> {}".format(
                message, 
                error.__class__.__name__ if hasattr(error, "__class__") and hasattr(error.__class__, "__name__") else error, 
                error.message if hasattr(error, "message") else error, 
                traceback.format_exc()
            )
        level = Level.SEVERE if error else Level.INFO
        self._logger.logp(level, name, stack, message)


class FileIngestModulePlus(IngestModulePlus, FileIngestModule):

    def __init__(self, moduleName, attributes):
        IngestModulePlus.__init__(self, moduleName, attributes)

    def startUp(self, context):
        IngestModulePlus.startUp(self, context)

    def process(self, file):
        pass

    def shutDown(self):
        IngestModulePlus.shutDown(self)


class DataSourceIngestModulePlus(IngestModulePlus, DataSourceIngestModule):

    def __init__(self, moduleName, attributes):
        IngestModulePlus.__init__(self, moduleName, attributes)
        self.progressBar = None
        self.files = None
        self.file_sources = None
        self.fileManager = None
        self.progress_count = None

    def startUp(self, context):
        IngestModulePlus.startUp(self, context)
        self.files = []
        self.file_sources = {}
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()
        self.progress_count = 0

    def process(self, dataSource, progressBar):
        self.progressBar = progressBar

         # we do not know how much work there is yet
        self.progressBar.switchToIndeterminate()

    def shutDown(self):
        IngestModulePlus.shutDown(self)

    def update_progress(self):
        if self.progress_count == 0:
            # now we know, how much work there will be
            self.progressBar.switchToDeterminate(len(self.files)+1)
        else:
            self.progress_count += 1
            self.progressBar.progress(self.progress_count)

    def get_mockup_file_for_multifile_artifacts(self, dataSource):
        # FIXME: slow
        files = sorted(self.fileManager.findFiles(dataSource, "%"), key=lambda x: x.getUniquePath())
        for file in files:
            if file.isFile() is False:
                return file
        raise IngestModuleException("Unexpected behavior: {} >> {} files >> no dir".format(
            ContentUtils.getSystemName(dataSource), len(files)))
