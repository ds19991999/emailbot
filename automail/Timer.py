#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import re
import time
import os


class TIME(object):
    """
    定义时间类
    """
    def __init__(self):
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None
        self.microsecond = None
        self.tzinfo = None

def str2time(time_str="2020-12-12 18:18:59"):
    """
    输入：str
    输出：TIME
    """
    time_temp_list = [None for x in range(8)]
    time_spl = re.sub("[ _:./]","-",time_str).split("-")
    for i in range(len(time_spl)):
        time_temp_list[i] = time_spl[i]

    time_temp = TIME()
    if time_temp_list[0] is not None:
        time_temp.year = int(time_temp_list[0])
    if time_temp_list[1] is not None:
        time_temp.month = int(time_temp_list[1])
    if time_temp_list[2] is not None:
        time_temp.day = int(time_temp_list[2])
    if time_temp_list[3] is not None:
        time_temp.hour = int(time_temp_list[3])
    if time_temp_list[4] is not None:
        time_temp.minute = int(time_temp_list[4])
    if time_temp_list[5] is not None:
        time_temp.second = int(time_temp_list[5])
    if time_temp_list[6] is not None:
        time_temp.microsecond = int(time_temp_list[6])
    if time_temp_list[7] is not None:
        time_temp.tzinfo = int(time_temp_list[7])
    return time_temp


def time_now():
    """
    输出：datetime
    """
    return datetime.datetime.now()


def set_time(time_temp):
    """
    输入: TIME 
    输出：datetime
    """
    time_now_temp = str2time(str(datetime.datetime.now()))
    if time_temp.year == None:
        time_temp.year = time_now_temp.year
    if time_temp.month == None:
        time_temp.month = time_now_temp.month
    if time_temp.day == None:
        time_temp.day = time_now_temp.day
    if time_temp.hour == None:
        time_temp.hour = time_now_temp.hour
    if time_temp.minute == None:
        time_temp.minute = time_now_temp.minute
    if time_temp.second == None:
        time_temp.second = time_now_temp.second
    if time_temp.microsecond == None:
        time_temp.microsecond = time_now_temp.microsecond
    if time_temp.tzinfo == None:
        time_temp.tzinfo = time_now_temp.tzinfo
    try:
        set_time_datetime = datetime.datetime(
            year = time_temp.year,
            month = time_temp.month,
            day = time_temp.day,
            hour = time_temp.hour,
            minute = time_temp.minute,
            second = time_temp.second,
            microsecond = time_temp.microsecond,
            tzinfo = time_temp.tzinfo
            )
        return set_time_datetime
    except Exception as msg:
        print("Error: " + str(msg))

