# -*- coding: utf-8 -*-

import re
from org.sleuthkit.datamodel import BlackboardAttribute

from utils.module import *


class ArtifactUtils:

    PREFIX_BASE = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]', '', PREFIX_MODULE).strip()).strip()

    TSK_TYPE_STR = BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING

    # ERRORS

    ERR_PARSE = '[PARSE ERROR, see logs]'
    ERR_BLOB = '[BLOB]'

    # ARTIFACTS

    PREFIX_ART = '{}TSK_ART_STEAMDECK_'.format(PREFIX_BASE)

    ART_BOOT_PARTITIONS = '{}BOOT_PARTITIONS'.format(PREFIX_ART)
    ART_DEVICE = '{}DEVICE'.format(PREFIX_ART)
    ART_FACTORY_RESET = '{}FACTORY_RESET'.format(PREFIX_ART)
    ART_FRIENDS = '{}FRIENDS'.format(PREFIX_ART)
    ART_GAMEAPPS = '{}GAMEAPPS'.format(PREFIX_ART)
    ART_LOG_ENTRIES = '{}LOG_ENTRIES'.format(PREFIX_ART)
    ART_LOG_FILES = '{}LOG_FILES'.format(PREFIX_ART)
    ART_POWERHISTORY = '{}POWERHISTORY'.format(PREFIX_ART)
    ART_SCREENSHOTS = '{}SCREENSHOTS'.format(PREFIX_ART)
    ART_SECRETS = '{}SECRETS'.format(PREFIX_ART)
    ART_USERS = '{}USERS'.format(PREFIX_ART)
    ART_WEB_COOKIES = '{}WEB_COOKIES'.format(PREFIX_ART)
    ART_WEB_QUOTAMANAGER = '{}WEB_QUOTAMANAGER'.format(PREFIX_ART)
    ART_WIFI = '{}WIFI'.format(PREFIX_ART)

    # ATTRIBUTES

    PREFIX_ATTR = '{}TSK_ATTR_STEAMDECK_'.format(PREFIX_BASE)

    ATTR_FILE_PATH = '{}FILE_PATH'.format(PREFIX_ATTR)
    ATTR_FILE_PATH_LOCAL = '{}FILE_PATH_LOCAL'.format(PREFIX_ATTR)
    ATTR_FILE_PATH_LOCAL_ABSOLUTE = '{}FILE_PATH_LOCAL_ABSOLUTE'.format(PREFIX_ATTR)
    ATTR_FILE_PATH_PARENT = '{}FILE_PATH_PARENT'.format(PREFIX_ATTR)
    ATTR_FILE_NAME = '{}FILE_NAME'.format(PREFIX_ATTR)
    ATTR_FILE_EXTENSION = '{}FILE_EXTENSION'.format(PREFIX_ATTR)
    ATTR_FILE_SIZE = '{}FILE_SIZE'.format(PREFIX_ATTR)
    ATTR_FILE_TYPE = '{}FILE_TYPE'.format(PREFIX_ATTR)
    ATTR_FILE_TYPE_MIME = '{}FILE_TYPE_MIME'.format(PREFIX_ATTR)
    ATTR_FILE_TYPE_META = '{}FILE_TYPE_META'.format(PREFIX_ATTR)
    ATTR_HASH_SHA256 = '{}HASH_SHA256'.format(PREFIX_ATTR)
    ATTR_HASH_SHA1 = '{}HASH_SHA1'.format(PREFIX_ATTR)
    ATTR_HASH_MD5 = '{}HASH_MD5'.format(PREFIX_ATTR)
    ATTR_EXISTS = '{}EXISTS'.format(PREFIX_ATTR)
    ATTR_IS_FILE = '{}IS_FILE'.format(PREFIX_ATTR)
    ATTR_IS_DIR = '{}IS_DIR'.format(PREFIX_ATTR)
    ATTR_IS_ROOT = '{}IS_ROOT'.format(PREFIX_ATTR)
    ATTR_IS_VIRTUAL = '{}IS_VIRTUAL'.format(PREFIX_ATTR)
    ATTR_HAS_FILESYSTEM = '{}HAS_FILESYSTEM'.format(PREFIX_ATTR)
    ATTR_TIME_A = '{}TIME_A'.format(PREFIX_ATTR)
    ATTR_TIME_M = '{}TIME_M'.format(PREFIX_ATTR)
    ATTR_TIME_CR = '{}TIME_CR'.format(PREFIX_ATTR)
    ATTR_TIME_C = '{}TIME_C'.format(PREFIX_ATTR)
    ATTR_DATE_A = '{}DATE_A'.format(PREFIX_ATTR)
    ATTR_DATE_M = '{}DATE_M'.format(PREFIX_ATTR)
    ATTR_DATE_CR = '{}DATE_CR'.format(PREFIX_ATTR)
    ATTR_DATE_C = '{}DATE_C'.format(PREFIX_ATTR)
    ATTR_APP_ID = '{}ID_APP'.format(PREFIX_ATTR)
    ATTR_FRIEND_ID = '{}ID_FRIEND'.format(PREFIX_ATTR)
    ATTR_STEAM_ID = '{}STEAM_ID'.format(PREFIX_ATTR)
    ATTR_NAME = '{}NAME'.format(PREFIX_ATTR)
    ATTR_NAME_HISTORY = '{}NAME_HISTORY'.format(PREFIX_ATTR)
    ATTR_AVATAR = '{}AVATAR'.format(PREFIX_ATTR)
    ATTR_TIMESTAMP = '{}TIMESTAMP'.format(PREFIX_ATTR)
    ATTR_TIMESTAMP_INTERPRETATION = '{}TIMESTAMP_INTERPRETATION'.format(PREFIX_ATTR)
    ATTR_SSID = '{}SSID'.format(PREFIX_ATTR)
    ATTR_PASSWORD = '{}PASSWORD'.format(PREFIX_ATTR)
    ATTR_OTHER = '{}OTHER'.format(PREFIX_ATTR)
    ATTR_8021X_IDENTITY = '{}8021X_IDENTITY'.format(PREFIX_ATTR)
    ATTR_ACCOUNT_NAME = '{}ACCOUNT_NAME'.format(PREFIX_ATTR)
    ATTR_PERSONA_NAME = '{}PERSONA_NAME'.format(PREFIX_ATTR)
    ATTR_ALLOW_AUTO_LOGIN = '{}ALLOW_AUTO_LOGIN'.format(PREFIX_ATTR)
    ATTR_MOST_RECENT = '{}MOST_RECENT'.format(PREFIX_ATTR)
    ATTR_REMEMBER_PASSWORD = '{}REMEMBER_PASSWORD'.format(PREFIX_ATTR)
    ATTR_WANTS_OFFLINE_MODE = '{}WANTS_OFFLINE_MODE'.format(PREFIX_ATTR)
    ATTR_SKIP_OFFLINE_MODE_WARNING = '{}SKIP_OFFLINE_MODE_WARNING'.format(PREFIX_ATTR)
    ATTR_EPOCH2DATE = '{}EPOCH2DATE'.format(PREFIX_ATTR)
    ATTR_DUPLICATE_CHECK_ID = '{}DUPLICATE_CHECK_ID'.format(PREFIX_ATTR)
    ATTR_INTERPRETATION = '{}INTERPRETATION'.format(PREFIX_ATTR)
    ATTR_OWNER_STEAM_ID = '{}OWNER_STEAM_ID'.format(PREFIX_ATTR)
    ATTR_INSTALLED = '{}INSTALLED'.format(PREFIX_ATTR)
    ATTR_RUNNING = '{}RUNNING'.format(PREFIX_ATTR)
    ATTR_UPDATING = '{}UPDATING'.format(PREFIX_ATTR)
    ATTR_AUTO_LOGIN_USER = '{}AUTO_LOGIN_USER'.format(PREFIX_ATTR)
    ATTR_LASTLOGIN = '{}LASTLOGIN'.format(PREFIX_ATTR)
    ATTR_LASTLOGIN_DATE = '{}LASTLOGIN_DATE'.format(PREFIX_ATTR)
    ATTR_LASTPLAYED = '{}LASTPLAYED'.format(PREFIX_ATTR)
    ATTR_LASTPLAYED_DATE = '{}LASTPLAYED_DATE'.format(PREFIX_ATTR)
    ATTR_LASTUPDATED = '{}LASTUPDATED'.format(PREFIX_ATTR)
    ATTR_LASTUPDATED_DATE = '{}LASTUPDATED_DATE'.format(PREFIX_ATTR)
    ATTR_AUTOCLOUD_LASTEXIT = '{}AUTOCLOUD_LASTEXIT'.format(PREFIX_ATTR)
    ATTR_AUTOCLOUD_LASTEXIT_DATE = '{}AUTOCLOUD_LASTEXIT_DATE'.format(PREFIX_ATTR)
    ATTR_AUTOCLOUD_LASTLAUNCH = '{}AUTOCLOUD_LASTLAUNCH'.format(PREFIX_ATTR)
    ATTR_AUTOCLOUD_LASTLAUNCH_DATE = '{}AUTOCLOUD_LASTLAUNCH_DATE'.format(PREFIX_ATTR)
    ATTR_PLAYTIME = '{}PLAYTIME'.format(PREFIX_ATTR)
    ATTR_PLAYTIME_2WKS = '{}PLAYTIME_2WKS'.format(PREFIX_ATTR)
    ATTR_CLOUD_LAST_SYNC_STATE = '{}CLOUD_LAST_SYNC_STATE'.format(PREFIX_ATTR)
    ATTR_CLOUD_QUOTA_FILES = '{}CLOUD_QUOTA_FILES'.format(PREFIX_ATTR)
    ATTR_CLOUD_QUOTA_BYTES = '{}CLOUD_QUOTA_BYTES'.format(PREFIX_ATTR)
    ATTR_CLOUD_USED_FILES = '{}CLOUD_USED_FILES'.format(PREFIX_ATTR)
    ATTR_CLOUD_USED_BYTES = '{}CLOUD_USED_BYTES'.format(PREFIX_ATTR)
    ATTR_DETECTED = '{}DETECTED'.format(PREFIX_ATTR)
    ATTR_SOURCES = '{}SOURCES'.format(PREFIX_ATTR)
    ATTR_BOOT_ATTEMPTS = '{}BOOT_ATTEMPTS'.format(PREFIX_ATTR)
    ATTR_BOOT_COUNT = '{}BOOT_COUNT'.format(PREFIX_ATTR)
    ATTR_BOOT_OTHER = '{}BOOT_OTHER'.format(PREFIX_ATTR)
    ATTR_BOOT_OTHER_DISABLED = '{}BOOT_OTHER_DISABLED'.format(PREFIX_ATTR)
    ATTR_BOOT_REQUESTED_AT = '{}BOOT_REQUESTED_AT'.format(PREFIX_ATTR)
    ATTR_BOOT_TIME = '{}BOOT_TIME'.format(PREFIX_ATTR)
    ATTR_BOOT_COMMENT = '{}BOOT_COMMENT'.format(PREFIX_ATTR)
    ATTR_BOOT_IMAGE_INVALID = '{}BOOT_IMAGE_INVALID'.format(PREFIX_ATTR)
    ATTR_BOOT_LOADER = '{}BOOT_LOADER'.format(PREFIX_ATTR)
    ATTR_BOOT_PARTITIONS = '{}BOOT_PARTITIONS'.format(PREFIX_ATTR)
    ATTR_BOOT_TITLE = '{}BOOT_TITLE'.format(PREFIX_ATTR)
    ATTR_BOOT_UPDATE = '{}BOOT_UPDATE'.format(PREFIX_ATTR)
    ATTR_BOOT_UPDATE_DISABLED = '{}BOOT_UPDATE_DISABLED'.format(PREFIX_ATTR)
    ATTR_BOOT_UPDATE_WINDOW_END = '{}BOOT_UPDATE_WINDOW_END'.format(PREFIX_ATTR)
    ATTR_BOOT_UPDATE_WINDOW_START = '{}BOOT_UPDATE_WINDOW_START'.format(PREFIX_ATTR)
    ATTR_SECRET_KIND = '{}SECRET_KIND'.format(PREFIX_ATTR)
    ATTR_SECRET_CONTEXT = '{}SECRET_CONTEXT'.format(PREFIX_ATTR)
    ATTR_SECRET_SECRET = '{}SECRET_SECRET'.format(PREFIX_ATTR)
    ATTR_SECRET_IDENTITY = '{}SECRET_IDENTITY'.format(PREFIX_ATTR)
    ATTR_SECRET_DESC = '{}SECRET_DESC'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_NAME = '{}WEB_COOKIE_NAME'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_VALUE = '{}WEB_COOKIE_VALUE'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_HOST = '{}WEB_COOKIE_HOST'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_PATH = '{}WEB_COOKIE_PATH'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_IS_SECURE = '{}WEB_COOKIE_IS_SECURE'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_IS_HTTPONLY = '{}WEB_COOKIE_IS_HTTPONLY'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_IS_PERSISTENT = '{}WEB_COOKIE_IS_PERSISTENT'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_HAS_EXPIRES = '{}WEB_COOKIE_HAS_EXPIRES'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_SAMESITE = '{}WEB_COOKIE_SAMESITE'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_CREATION_UTC = '{}WEB_COOKIE_CREATION_UTC'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_EXPIRES_UTC = '{}WEB_COOKIE_EXPIRES_UTC'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_LAST_ACCESS_UTC = '{}WEB_COOKIE_LAST_ACCESS_UTC'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_PRIORITY = '{}WEB_COOKIE_PRIORITY'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_SOURCE_SCHEME = '{}WEB_COOKIE_SOURCE_SCHEME'.format(PREFIX_ATTR)
    ATTR_WEB_COOKIE_ENCRYPTED_VALUE = '{}WEB_COOKIE_ENCRYPTED_VALUE'.format(PREFIX_ATTR)
    ATTR_WEB_QUOTAMANAGER_ORIGIN = '{}WEB_QUOTAMANAGER_ORIGIN'.format(PREFIX_ATTR)
    ATTR_WEB_QUOTAMANAGER_TYPE = '{}WEB_QUOTAMANAGER_TYPE'.format(PREFIX_ATTR)
    ATTR_WEB_QUOTAMANAGER_USED_COUNT = '{}WEB_QUOTAMANAGER_USED_COUNT'.format(PREFIX_ATTR)
    ATTR_WEB_QUOTAMANAGER_LAST_ACCESS_UTC = '{}WEB_QUOTAMANAGER_LAST_ACCESS_UTC'.format(PREFIX_ATTR)
    ATTR_WEB_QUOTAMANAGER_LAST_MODIFIED_UTC = '{}WEB_QUOTAMANAGER_LAST_MODIFIED_UTC'.format(PREFIX_ATTR)
    ATTR_LOG_TIMESTAMP = '{}LOG_TIMESTAMP'.format(PREFIX_ATTR)
    ATTR_LOG_MESSAGE = '{}LOG_MESSAGE'.format(PREFIX_ATTR)
    ATTR_DEVICE_KEY = '{}DEVICE_KEY'.format(PREFIX_ATTR)
    ATTR_DEVICE_VALUE = '{}DEVICE_VALUE'.format(PREFIX_ATTR)
    ATTR_POWERHISTORY_TIMESTAMP = '{}POWERHISTORY_TIMESTAMP'.format(PREFIX_ATTR)
    ATTR_POWERHISTORY_TYPE = '{}POWERHISTORY_TYPE'.format(PREFIX_ATTR)
    ATTR_POWERHISTORY_VALUE = '{}POWERHISTORY_VALUE'.format(PREFIX_ATTR)
    ATTR_POWERHISTORY_STATUS = '{}POWERHISTORY_STATUS'.format(PREFIX_ATTR)

    ATTRIBUTES_FILE = {
        ATTR_FILE_PATH: {'type': TSK_TYPE_STR, 'label': 'File path'},
        ATTR_FILE_PATH_LOCAL: {'type': TSK_TYPE_STR, 'label': 'File path local'},
        ATTR_FILE_PATH_LOCAL_ABSOLUTE: {'type': TSK_TYPE_STR, 'label': 'File path local absolute'},
        ATTR_FILE_PATH_PARENT: {'type': TSK_TYPE_STR, 'label': 'File path parent'},
        ATTR_FILE_NAME: {'type': TSK_TYPE_STR, 'label': 'File name'},
        ATTR_FILE_EXTENSION: {'type': TSK_TYPE_STR, 'label': 'File extension'},
        ATTR_FILE_SIZE: {'type': TSK_TYPE_STR, 'label': 'File size'},
        ATTR_FILE_TYPE: {'type': TSK_TYPE_STR, 'label': 'File type'},
        ATTR_FILE_TYPE_MIME: {'type': TSK_TYPE_STR, 'label': 'File type MIME'},
        ATTR_FILE_TYPE_META: {'type': TSK_TYPE_STR, 'label': 'File type meta'},
        ATTR_HASH_SHA256: {'type': TSK_TYPE_STR, 'label': 'SHA256'},
        ATTR_HASH_SHA1: {'type': TSK_TYPE_STR, 'label': 'SHA1'},
        ATTR_HASH_MD5: {'type': TSK_TYPE_STR, 'label': 'MD5'},
        ATTR_EXISTS: {'type': TSK_TYPE_STR, 'label': 'Exists'},
        ATTR_IS_FILE: {'type': TSK_TYPE_STR, 'label': 'Is file'},
        ATTR_IS_DIR: {'type': TSK_TYPE_STR, 'label': 'Is directory'},
        ATTR_IS_ROOT: {'type': TSK_TYPE_STR, 'label': 'Is root'},
        ATTR_IS_VIRTUAL: {'type': TSK_TYPE_STR, 'label': 'Is virtual'},
        ATTR_HAS_FILESYSTEM: {'type': TSK_TYPE_STR, 'label': 'Has filesystem'},
        ATTR_TIME_A: {'type': TSK_TYPE_STR, 'label': 'Accessed'},
        ATTR_TIME_M: {'type': TSK_TYPE_STR, 'label': 'Modified'},
        ATTR_TIME_CR: {'type': TSK_TYPE_STR, 'label': 'Created'},
        ATTR_TIME_C: {'type': TSK_TYPE_STR, 'label': 'Changed'},
        ATTR_DATE_A: {'type': TSK_TYPE_STR, 'label': 'Accessed (Date)'},
        ATTR_DATE_M: {'type': TSK_TYPE_STR, 'label': 'Modified (Date)'},
        ATTR_DATE_CR: {'type': TSK_TYPE_STR, 'label': 'Created (Date)'},
        ATTR_DATE_C: {'type': TSK_TYPE_STR, 'label': 'Changed (Date)'},
    }
    ATTRIBUTES_FILE_KEYS = list(ATTRIBUTES_FILE.keys())

    ATTRIBUTES_CUSTOM = {
        ATTR_DUPLICATE_CHECK_ID: {'type': TSK_TYPE_STR, 'label': 'Duplicate Check ID'},
        ATTR_EPOCH2DATE: {'type': TSK_TYPE_STR, 'label': 'Timestamp (Epoch to Date)'},
        ATTR_TIMESTAMP_INTERPRETATION: {'type': TSK_TYPE_STR, 'label': 'Timestamp Interpretation'},
        ATTR_APP_ID: {'type': TSK_TYPE_STR, 'label': 'App ID'},
        ATTR_FRIEND_ID: {'type': TSK_TYPE_STR, 'label': 'Friend ID'},
        ATTR_TIMESTAMP: {'type': TSK_TYPE_STR, 'label': 'Timestamp'},
        ATTR_SSID: {'type': TSK_TYPE_STR, 'label': 'SSID'},
        ATTR_PASSWORD: {'type': TSK_TYPE_STR, 'label': 'Password'},
        ATTR_OTHER: {'type': TSK_TYPE_STR, 'label': 'Other'},
        ATTR_8021X_IDENTITY: {'type': TSK_TYPE_STR, 'label': 'Identity (802.1x)'},
        ATTR_STEAM_ID: {'type': TSK_TYPE_STR, 'label': 'Steam ID'},
        ATTR_ACCOUNT_NAME: {'type': TSK_TYPE_STR, 'label': 'Account Name'},
        ATTR_PERSONA_NAME: {'type': TSK_TYPE_STR, 'label': 'Persona Name'},
        ATTR_ALLOW_AUTO_LOGIN: {'type': TSK_TYPE_STR, 'label': 'Allow AutoLogin'},
        ATTR_MOST_RECENT: {'type': TSK_TYPE_STR, 'label': 'Most Recent'},
        ATTR_REMEMBER_PASSWORD: {'type': TSK_TYPE_STR, 'label': 'Remember Password'},
        ATTR_WANTS_OFFLINE_MODE: {'type': TSK_TYPE_STR, 'label': 'Wants Offline Mode'},
        ATTR_SKIP_OFFLINE_MODE_WARNING: {'type': TSK_TYPE_STR, 'label': 'Skip Offline Mode Warning'},
        ATTR_INTERPRETATION: {'type': TSK_TYPE_STR, 'label': 'Interpretation'},
        ATTR_NAME: {'type': TSK_TYPE_STR, 'label': 'Name'},
        ATTR_NAME_HISTORY: {'type': TSK_TYPE_STR, 'label': 'Name History'},
        ATTR_AVATAR: {'type': TSK_TYPE_STR, 'label': 'Avatar'},
        ATTR_OWNER_STEAM_ID: {'type': TSK_TYPE_STR, 'label': 'Owner (Steam ID)'},
        ATTR_INSTALLED: {'type': TSK_TYPE_STR, 'label': 'Installed'},
        ATTR_RUNNING: {'type': TSK_TYPE_STR, 'label': 'Running'},
        ATTR_UPDATING: {'type': TSK_TYPE_STR, 'label': 'Updating'},
        ATTR_AUTO_LOGIN_USER: {'type': TSK_TYPE_STR, 'label': 'AutoLogin User'},
        ATTR_LASTPLAYED_DATE: {'type': TSK_TYPE_STR, 'label': 'Last Played'},
        ATTR_LASTUPDATED_DATE: {'type': TSK_TYPE_STR, 'label': 'Last Updated'},
        ATTR_AUTOCLOUD_LASTEXIT_DATE: {'type': TSK_TYPE_STR, 'label': 'Last Exit (Autocloud)'},
        ATTR_AUTOCLOUD_LASTLAUNCH_DATE: {'type': TSK_TYPE_STR, 'label': 'Last Launch (Autocloud)'},
        ATTR_LASTPLAYED: {'type': TSK_TYPE_STR, 'label': 'Last Played (Epoch)'},
        ATTR_LASTUPDATED: {'type': TSK_TYPE_STR, 'label': 'Last Updated (Epoch)'},
        ATTR_AUTOCLOUD_LASTEXIT: {'type': TSK_TYPE_STR, 'label': 'Last Exit (Autocloud, Epoch)'},
        ATTR_AUTOCLOUD_LASTLAUNCH: {'type': TSK_TYPE_STR, 'label': 'Last Launch (Autocloud, Epoch)'},
        ATTR_PLAYTIME: {'type': TSK_TYPE_STR, 'label': 'Playtime'},
        ATTR_PLAYTIME_2WKS: {'type': TSK_TYPE_STR, 'label': 'Playtime (2 weeks)'},
        ATTR_CLOUD_LAST_SYNC_STATE: {'type': TSK_TYPE_STR, 'label': 'Last Sync State (Cloud)'},
        ATTR_CLOUD_QUOTA_FILES: {'type': TSK_TYPE_STR, 'label': 'Quota Files (Cloud)'},
        ATTR_CLOUD_QUOTA_BYTES: {'type': TSK_TYPE_STR, 'label': 'Quota Bytes (Cloud)'},
        ATTR_CLOUD_USED_FILES: {'type': TSK_TYPE_STR, 'label': 'Used Files (Cloud)'},
        ATTR_CLOUD_USED_BYTES: {'type': TSK_TYPE_STR, 'label': 'Used Bytes (Cloud)'},
        ATTR_DETECTED: {'type': TSK_TYPE_STR, 'label': 'Detected'},
        ATTR_SOURCES: {'type': TSK_TYPE_STR, 'label': 'Sources'},
        ATTR_LASTLOGIN: {'type': TSK_TYPE_STR, 'label': 'Last Login (Epoch)'},
        ATTR_LASTLOGIN_DATE: {'type': TSK_TYPE_STR, 'label': 'Last Login'},
        ATTR_BOOT_ATTEMPTS: {'type': TSK_TYPE_STR, 'label': 'Boot Attempts'},
        ATTR_BOOT_COUNT: {'type': TSK_TYPE_STR, 'label': 'Boot Count'},
        ATTR_BOOT_OTHER: {'type': TSK_TYPE_STR, 'label': 'Boot Other'},
        ATTR_BOOT_OTHER_DISABLED: {'type': TSK_TYPE_STR, 'label': 'Boot Other Disabled'},
        ATTR_BOOT_REQUESTED_AT: {'type': TSK_TYPE_STR, 'label': 'Boot Requested At'},
        ATTR_BOOT_TIME: {'type': TSK_TYPE_STR, 'label': 'Boot Time'},
        ATTR_BOOT_COMMENT: {'type': TSK_TYPE_STR, 'label': 'Comment'},
        ATTR_BOOT_IMAGE_INVALID: {'type': TSK_TYPE_STR, 'label': 'Image Invalid'},
        ATTR_BOOT_LOADER: {'type': TSK_TYPE_STR, 'label': 'Loader'},
        ATTR_BOOT_PARTITIONS: {'type': TSK_TYPE_STR, 'label': 'Partitions'},
        ATTR_BOOT_TITLE: {'type': TSK_TYPE_STR, 'label': 'Title'},
        ATTR_BOOT_UPDATE: {'type': TSK_TYPE_STR, 'label': 'Update'},
        ATTR_BOOT_UPDATE_DISABLED: {'type': TSK_TYPE_STR, 'label': 'Update Disabled'},
        ATTR_BOOT_UPDATE_WINDOW_END: {'type': TSK_TYPE_STR, 'label': 'Update Window End'},
        ATTR_BOOT_UPDATE_WINDOW_START: {'type': TSK_TYPE_STR, 'label': 'Update Window Start'},
        ATTR_SECRET_KIND: {'type': TSK_TYPE_STR, 'label': 'Kind'},
        ATTR_SECRET_CONTEXT: {'type': TSK_TYPE_STR, 'label': 'Context'},
        ATTR_SECRET_SECRET: {'type': TSK_TYPE_STR, 'label': 'Secret'},
        ATTR_SECRET_IDENTITY: {'type': TSK_TYPE_STR, 'label': 'Identity'},
        ATTR_SECRET_DESC: {'type': TSK_TYPE_STR, 'label': 'Description'},
        ATTR_WEB_COOKIE_NAME: {'type': TSK_TYPE_STR, 'label': 'Name'},
        ATTR_WEB_COOKIE_VALUE: {'type': TSK_TYPE_STR, 'label': 'Value'},
        ATTR_WEB_COOKIE_HOST: {'type': TSK_TYPE_STR, 'label': 'Host'},
        ATTR_WEB_COOKIE_PATH: {'type': TSK_TYPE_STR, 'label': 'Path'},
        ATTR_WEB_COOKIE_IS_SECURE: {'type': TSK_TYPE_STR, 'label': 'Is Secure'},
        ATTR_WEB_COOKIE_IS_HTTPONLY: {'type': TSK_TYPE_STR, 'label': 'Is HttpOnly'},
        ATTR_WEB_COOKIE_IS_PERSISTENT: {'type': TSK_TYPE_STR, 'label': 'Is Persistent'},
        ATTR_WEB_COOKIE_HAS_EXPIRES: {'type': TSK_TYPE_STR, 'label': 'Has Expires'},
        ATTR_WEB_COOKIE_SAMESITE: {'type': TSK_TYPE_STR, 'label': 'Samesite'},
        ATTR_WEB_COOKIE_CREATION_UTC: {'type': TSK_TYPE_STR, 'label': 'Creation (UTC)'},
        ATTR_WEB_COOKIE_EXPIRES_UTC: {'type': TSK_TYPE_STR, 'label': 'Expires (UTC)'},
        ATTR_WEB_COOKIE_LAST_ACCESS_UTC: {'type': TSK_TYPE_STR, 'label': 'Last Access (UTC)'},
        ATTR_WEB_COOKIE_PRIORITY: {'type': TSK_TYPE_STR, 'label': 'Priority'},
        ATTR_WEB_COOKIE_SOURCE_SCHEME: {'type': TSK_TYPE_STR, 'label': 'Source Scheme'},
        ATTR_WEB_COOKIE_ENCRYPTED_VALUE: {'type': TSK_TYPE_STR, 'label': 'Encrypted Value'},
        ATTR_WEB_QUOTAMANAGER_ORIGIN: {'type': TSK_TYPE_STR, 'label': 'Origin'},
        ATTR_WEB_QUOTAMANAGER_TYPE: {'type': TSK_TYPE_STR, 'label': 'Type'},
        ATTR_WEB_QUOTAMANAGER_USED_COUNT: {'type': TSK_TYPE_STR, 'label': 'Used Count'},
        ATTR_WEB_QUOTAMANAGER_LAST_ACCESS_UTC: {'type': TSK_TYPE_STR, 'label': 'Last Access (UTC)'},
        ATTR_WEB_QUOTAMANAGER_LAST_MODIFIED_UTC: {'type': TSK_TYPE_STR, 'label': 'Last Modified (UTC)'},
        ATTR_LOG_TIMESTAMP: {'type': TSK_TYPE_STR, 'label': 'Timestamp'},
        ATTR_LOG_MESSAGE: {'type': TSK_TYPE_STR, 'label': 'Message'},
        ATTR_DEVICE_KEY: {'type': TSK_TYPE_STR, 'label': 'Information'},
        ATTR_DEVICE_VALUE: {'type': TSK_TYPE_STR, 'label': 'Value'},
        
        ATTR_POWERHISTORY_TIMESTAMP: {'type': TSK_TYPE_STR, 'label': 'Timestamp'},
        ATTR_POWERHISTORY_TYPE: {'type': TSK_TYPE_STR, 'label': 'Type'},
        ATTR_POWERHISTORY_VALUE: {'type': TSK_TYPE_STR, 'label': 'Value'},
        ATTR_POWERHISTORY_STATUS: {'type': TSK_TYPE_STR, 'label': 'Status'},
    }
    ATTRIBUTES_CUSTOM_KEYS = list(ATTRIBUTES_CUSTOM.keys())

    @staticmethod
    def get_all_attributes():
        attributes = {}
        attributes.update(ArtifactUtils.ATTRIBUTES_CUSTOM)
        attributes.update(ArtifactUtils.ATTRIBUTES_FILE)
        return attributes

    @staticmethod
    def get_attribute_type(key):
        attributes = ArtifactUtils.get_all_attributes()
        assert key in attributes, "Key `{}` not in {}".format(key, sorted(attributes.keys()))
        return attributes[key]['type']

    @staticmethod
    def get_attribute_label(key):
        attributes = ArtifactUtils.get_all_attributes()
        assert key in attributes, "Key `{}` not in {}".format(key, sorted(attributes.keys()))
        return attributes[key]['label']

    @staticmethod
    def get_module_artifact_label(module):
        if module == MODULE_BOOT_PARTITIONS:
            return ArtifactUtils.ART_BOOT_PARTITIONS
        if module == MODULE_DEVICE:
            return ArtifactUtils.ART_DEVICE
        if module == MODULE_FACTORY_RESET:
            return ArtifactUtils.ART_FACTORY_RESET
        if module == MODULE_FRIENDS:
            return ArtifactUtils.ART_FRIENDS
        if module == MODULE_GAMEAPPS:
            return ArtifactUtils.ART_GAMEAPPS
        if module == MODULE_LOG_ENTRIES:
            return ArtifactUtils.ART_LOG_ENTRIES
        if module == MODULE_LOG_FILES:
            return ArtifactUtils.ART_LOG_FILES
        if module == MODULE_POWER_HISTORY:
            return ArtifactUtils.ART_POWERHISTORY
        if module == MODULE_SCREENSHOTS:
            return ArtifactUtils.ART_SCREENSHOTS
        if module == MODULE_SECRETS:
            return ArtifactUtils.ART_SECRETS
        if module == MODULE_USERS:
            return ArtifactUtils.ART_USERS
        if module == MODULE_WEB_COOKIES:
            return ArtifactUtils.ART_WEB_COOKIES
        if module == MODULE_WEB_QUOTAMANAGER:
            return ArtifactUtils.ART_WEB_QUOTAMANAGER
        if module == MODULE_WIFI:
            return ArtifactUtils.ART_WIFI
        
        raise Exception("Unknown module: {}".format(module))
