# -*- coding: utf-8 -*-

import os
import re
import jarray
import tempfile
import hashlib
import ConfigParser
import xml.etree.ElementTree as ET
from java.io import File
from java.lang import Class
from java.sql import DriverManager
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.datamodel import ContentUtils

from utils.artifact import ArtifactUtils
from utils.timestamp import TimestampUtils
from utils.thirdparty import vdf
from utils.thirdparty.vdfutils.vdfutils import parse_vdf as vdfutils_parse_vdf


class TSKFileUtils:

    @staticmethod
    def is_slack_file(file):
        return file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.SLACK

    @staticmethod
    def is_non_file(file):
        return (
            (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNALLOC_BLOCKS)
            or (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNUSED_BLOCKS)
            or (file.isFile() is False)
        )
    
    @staticmethod
    def create_duplicate_check_id(data, attributes):
        values = []
        for attr in sorted(attributes):
            if attr == ArtifactUtils.ATTR_DUPLICATE_CHECK_ID:
                continue
            if attr in data:
                values.append(str(data[attr]))
            else:
                values.append("")
        return hashlib.sha256(", ".join(values)).hexdigest()

    @staticmethod
    def open_file(file, case=None, return_path=False):
        if case:
            # write contents from TSK File object to temporary file
            filepath = os.path.join(case.getTempDirectory(), "{}.db".format(file.getId()))
            ContentUtils.writeToFile(file, File(filepath))
            fh = open(filepath, "rb")
            fh.seek(0)

            if return_path:
                return fh, filepath

        else:
            # read contents from TSK File object into jarray buffer
            buffer = jarray.zeros(file.getSize(), "b")
            file.read(buffer, 0, file.getSize())

            # write contents from buffer into temporary file
            fh = tempfile.NamedTemporaryFile(delete=False)
            fh.write(buffer)
            fh.seek(0)

        return fh

    @staticmethod
    def close_file(fh):
        if fh:
            fh.close()
            if hasattr(fh, "name"):
                os.remove(fh.name)

    @staticmethod
    def open_sqlite_file(file, case):
        fh, path_tmp = TSKFileUtils.open_file(file=file, case=case, return_path=True)
        Class.forName("org.sqlite.JDBC").newInstance()
        dbConn = DriverManager.getConnection("jdbc:sqlite:{}".format(path_tmp))
        return dbConn, fh
    
    @staticmethod
    def close_sqlite_file(dbConn, fh):
        if dbConn:
            dbConn.close()
        TSKFileUtils.close_file(fh)

    @staticmethod
    def parse_xml_file(file, case=None):
        fh = TSKFileUtils.open_file(file, case=case)
        tree = ET.fromstring(fh.read())
        TSKFileUtils.close_file(fh)
        return tree

    @staticmethod
    def parse_vdf_file(file, case=None):
        fh = None
        data = {}
        
        try:
            fh = TSKFileUtils.open_file(file, case=case)
            try:
                data = vdfutils_parse_vdf(fh.read())
            except:
                try:
                    data = vdf.loads(fh.read())
                finally:
                    pass

        finally:
            if fh:
                TSKFileUtils.close_file(fh)
                        
        return data

    @staticmethod
    def parse_config_file(file, lowercase=True):
        # read config file
        fh = TSKFileUtils.open_file(file)
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(fh)
        TSKFileUtils.close_file(fh)

        # read config as dictionary, flatten nested dictionary, and alter keys 
        data = TSKFileUtils.flatten_dict(
            {s:dict(config.items(s)) for s in config.sections()}, lowercase=lowercase)

        return data

    @staticmethod
    def parse_boot_config(file):
        # read boot config file
        fh = TSKFileUtils.open_file(file)

        # parse boot config file
        config = {}
        for line in fh.readlines():
            if line.strip() == "":
                continue
            m = re.match(r'([^:]*):\s+(.*)\n', line)
            if not m:
                continue
            assert len(m.groups()) == 2, "{} > {}".format(line, m.groups())
            key, value = m.groups()
            config[key] = value
        
        TSKFileUtils.close_file(fh)

        # parse timestamps
        if 'boot-time' in config and config['boot-time'] != '0':
            config['boot-time'] = \
                TimestampUtils.bootconfig_timestamp_to_date_str(config['boot-time'])

        if 'boot-requested-at' in config and config['boot-requested-at'] != '0':
            config['boot-requested-at'] = \
                TimestampUtils.bootconfig_timestamp_to_date_str(config['boot-requested-at'])

        return config
    
    @staticmethod
    def flatten_dict(d, pkey='', sep='_', lowercase=True):
        # modified: https://www.askpython.com/python/dictionary/flatten-nested-dictionary-via-compressing-keys
        items = []
        for k, v in d.items():
            key = "{}{}{}".format(pkey, sep, k) if pkey else k
            key = re.sub(r"[^_a-zA-Z0-9]", "_", key).strip()
            if lowercase:
                key = key.lower()
            if isinstance(v, dict):
                items.extend(
                    TSKFileUtils.flatten_dict(v, key, sep=sep, lowercase=lowercase).items())
            else:
                items.append((key, v))
        return dict(items)

    @staticmethod
    def get_file_info(file):
        info = {}

        try:
            info[ArtifactUtils.ATTR_FILE_PATH] = str(file.getUniquePath())
        except:
            info[ArtifactUtils.ATTR_FILE_PATH] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_PATH_LOCAL] = str(file.getLocalPath())
        except:
            info[ArtifactUtils.ATTR_FILE_PATH_LOCAL] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_PATH_LOCAL_ABSOLUTE] = str(file.getLocalAbsPath())
        except:
            info[ArtifactUtils.ATTR_FILE_PATH_LOCAL_ABSOLUTE] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_PATH_PARENT] = str(file.getParentPath())
        except:
            info[ArtifactUtils.ATTR_FILE_PATH_PARENT] = ""

        try:
            info[ArtifactUtils.ATTR_FILE_NAME] = str(file.getName())
        except:
            info[ArtifactUtils.ATTR_FILE_NAME] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_EXTENSION] = str(file.getNameExtension())
        except:
            info[ArtifactUtils.ATTR_FILE_EXTENSION] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_SIZE] = str(file.getSize())
        except:
            info[ArtifactUtils.ATTR_FILE_SIZE] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_TYPE] = str(file.getType())
        except:
            info[ArtifactUtils.ATTR_FILE_TYPE] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_TYPE_MIME] = str(file.getMIMEType())
        except:
            info[ArtifactUtils.ATTR_FILE_TYPE_MIME] = ""
        try:
            info[ArtifactUtils.ATTR_FILE_TYPE_META] = str(file.getMetaTypeAsString())
        except:
            info[ArtifactUtils.ATTR_FILE_TYPE_META] = ""

        try:
            info[ArtifactUtils.ATTR_HASH_SHA256] = str(file.getSha256Hash())
        except:
            info[ArtifactUtils.ATTR_HASH_SHA256] = ""
        try:
            info[ArtifactUtils.ATTR_HASH_SHA1] = str(file.getSha1Hash())
        except:
            info[ArtifactUtils.ATTR_HASH_SHA1] = ""
        try:
            info[ArtifactUtils.ATTR_HASH_MD5] = str(file.getMd5Hash())
        except:
            info[ArtifactUtils.ATTR_HASH_MD5] = ""

        try:
            info[ArtifactUtils.ATTR_EXISTS] = str(file.exists())
        except:
            info[ArtifactUtils.ATTR_EXISTS] = ""
        try:
            info[ArtifactUtils.ATTR_IS_FILE] = str(file.isFile())
        except:
            info[ArtifactUtils.ATTR_IS_FILE] = ""
        try:
            info[ArtifactUtils.ATTR_IS_DIR] = str(file.isDir())
        except:
            info[ArtifactUtils.ATTR_IS_DIR] = ""
        try:
            info[ArtifactUtils.ATTR_IS_ROOT] = str(file.isRoot())
        except:
            info[ArtifactUtils.ATTR_IS_ROOT] = ""
        try:
            info[ArtifactUtils.ATTR_IS_VIRTUAL] = str(file.isVirtual())
        except:
            info[ArtifactUtils.ATTR_IS_VIRTUAL] = ""
        try:
            info[ArtifactUtils.ATTR_HAS_FILESYSTEM] = str(file.hasFileSystem())
        except:
            info[ArtifactUtils.ATTR_HAS_FILESYSTEM] = ""
        
        try:
            info[ArtifactUtils.ATTR_TIME_A] = str(file.getAtime())
        except:
            info[ArtifactUtils.ATTR_TIME_A] = ""
        try:
            info[ArtifactUtils.ATTR_TIME_M] = str(file.getMtime())
        except:
            info[ArtifactUtils.ATTR_TIME_M] = ""
        try:
            info[ArtifactUtils.ATTR_TIME_CR] = str(file.getCrtime())
        except:
            info[ArtifactUtils.ATTR_TIME_CR] = ""
        try:
            info[ArtifactUtils.ATTR_TIME_C] = str(file.getCtime())
        except:
            info[ArtifactUtils.ATTR_TIME_C] = ""

        try:
            info[ArtifactUtils.ATTR_DATE_A] = str(file.getAtimeAsDate())
        except:
            info[ArtifactUtils.ATTR_DATE_A] = ""
        try:
            info[ArtifactUtils.ATTR_DATE_M] = str(file.getMtimeAsDate())
        except:
            info[ArtifactUtils.ATTR_DATE_M] = ""
        try:
            info[ArtifactUtils.ATTR_DATE_CR] = str(file.getCrtimeAsDate())
        except:
            info[ArtifactUtils.ATTR_DATE_CR] = ""
        try:
            info[ArtifactUtils.ATTR_DATE_C] = str(file.getCtimeAsDate())
        except:
            info[ArtifactUtils.ATTR_DATE_C] = ""

        return info
