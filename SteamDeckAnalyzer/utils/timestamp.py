# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta


class TimestampUtils:

    @staticmethod
    def epoch_to_date(epoch_seconds):
        TimestampUtils.__assert_epoch_seconds(epoch_seconds)
        return datetime.fromtimestamp(float(epoch_seconds)).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def epoch_to_date_str(epoch_seconds):
        return str(TimestampUtils.epoch_to_date(epoch_seconds))
    
    @staticmethod
    def webkit_to_date_str(microseconds):
        # see: https://www.epochconverter.com/webkit
        # quote: "It's a 64-bit value for microseconds since Jan 1, 1601 00:00 UTC."
        epoch_start = datetime(1601, 1, 1)
        delta = timedelta(microseconds=int(microseconds))
        return (epoch_start + delta).strftime('%Y-%m-%d %H:%M:%S.%f')

    
    @staticmethod
    def bootconfig_timestamp_to_date_str(timestamp):
        assert re.match(r'^\d{14}$', timestamp), "{}".format(timestamp)
        return datetime.strptime(timestamp, '%Y%m%d%H%M%S')

    @staticmethod   
    def __assert_epoch_seconds(epoch_seconds):
        assert isinstance(epoch_seconds, float) or isinstance(epoch_seconds, int) or isinstance(epoch_seconds, str), "{}: {}".format(type(epoch_seconds), epoch_seconds)
