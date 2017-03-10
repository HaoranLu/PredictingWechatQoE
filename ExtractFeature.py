import json
from pprint import pprint
import numpy as np
from decimal import *

_PrecisionStandard = Decimal('1234567890.123456789')


def ExtractPackge_func(Packages, timePoint, windowSize):
    indexList = []
    for i, pk in enumerate(Packages):
        timestamp = pk['_source']['layers']['frame']['frame.time_relative']
        getcontext().prec = 19
        timestamp = Decimal(timestamp)
        timePoint = Decimal(timePoint)
        windowSize = Decimal(windowSize)
        if (timestamp <= timePoint) and (timestamp >= timePoint - windowSize):
            indexList.append(i)
    PackageList = []
    for i in indexList:
        PackageList.append(Packages[i])
    return PackageList


def Avg_Throughtput_func(PacketList, windowSize):
    size = len(PacketList)
    total = 0
    for pp in PacketList:
        total = total + int(pp['_source']['layers']['frame']['frame.cap_len'])
    avg = float(total) / size / windowSize
    return avg


def Var_PacketSize_func(PacketList):
    size = len(PacketList)
    sizeList = []
    total = 0
    totalof2 = 0
    for pp in PacketList:
        s = int(pp['_source']['layers']['frame']['frame.cap_len'])
        sizeList.append(s)
        total = total + s
        totalof2 = totalof2 + s * s
    if size > 1:
        variance = (totalof2 - (total * total) / size) / (size - 1)
        return variance
    else:
        return 0


def Avg_ArrivingInterval_func(PacketList, windowSize):
    intervalList = []
    total = Decimal()
    for i, pk in enumerate(PacketList):
        timestamp = pk['_source']['layers']['frame']['frame.time_epoch']
        if i > 0:
            pre_timestamp = PacketList[
                i - 1]['_source']['layers']['frame']['frame.time_epoch']
            getcontext().prec = 19
            timestamp = Decimal(timestamp)
            pre_timestamp = Decimal(pre_timestamp)
            interval = (timestamp - pre_timestamp).quantize(_PrecisionStandard)
            intervalList.append(interval)
            total = total + interval
    size = len(intervalList)
    if size > 0:
        return total / size
    else:
        return windowSize/2.0


def Var_ArrivingInterval_func(PacketList):
    intervalList = []
    total = Decimal()
    totalof2 = Decimal()
    for i, pk in enumerate(PacketList):
        timestamp = pk['_source']['layers']['frame']['frame.time_epoch']
        if i > 0:
            pre_timestamp = PacketList[
                i - 1]['_source']['layers']['frame']['frame.time_epoch']
            getcontext().prec = 19
            timestamp = Decimal(timestamp)
            pre_timestamp = Decimal(pre_timestamp)
            interval = (timestamp - pre_timestamp).quantize(_PrecisionStandard)
            intervalList.append(interval)
            total = total + interval
            totalof2 = totalof2 + interval * interval
    size = len(intervalList)
    if size > 1:
        variance = (totalof2 - (total * total) / size) / (size - 1)
        return variance
    else:
        return 0


def Avg_RTT_func(PacketList):
    size = len(PacketList)
    if size <= 0:
        return 100
    total = 0
    num = 0
    for pk in PacketList:
        pkTyep = pk['_source']['layers']['icmp']['icmp.type']
        if pkTyep == '0':  # is a icmp response
            rtt = pk['_source']['layers']['icmp']['icmp.resptime']
            total = total + float(rtt)
            num = num + 1
    if num > 0:
        Avg_RTT = total / num
        return Avg_RTT
    return 100
