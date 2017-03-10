import json
import numpy as np
import ExtractFeature as EF
import os
from mmap import mmap
from decimal import *
hxq = 'HXQ'
lhr = 'LHR'
DataFolder = 'Data'
FolderIndex = [3, 4, 5]
_FolderIndex = [1, 2, 3, 4, 5]
uploadName = 'Upload'
downloadName = 'Download'
icmpName = 'icmp'
lowQOEName = 'time.txt'
windowSize = 5.0
goodTimepointOffset = 0.3
good = 1
bad = 0


class data:
    'ndarray x and y for svm'
    x_data = np.ndarray
    y_target = np.ndarray
    goodData = np.ndarray
    badData = np.ndarray

    def __init__(self, x, y, good, bad):
        self.x_data = x
        self.y_target = y
        self.goodData = good
        self.badData = bad


def getData():
    fileRoot_lhr = DataFolder + '/' + lhr
    fileRoot_hxq = DataFolder + '/' + hxq
    fileRootlist = [fileRoot_lhr, fileRoot_hxq]
    x = np.array([])
    x = x.reshape(0, 9)
    y = np.array([])
    goodFeature = np.array([])
    goodFeature = goodFeature.reshape(0, 9)
    badFeature = np.array([])
    badFeature = badFeature.reshape(0, 9)
    for fileroot in fileRootlist:
        for fi in FolderIndex:
            for _fi in _FolderIndex:
                # get timepoint list
                fullPath = fileroot + '/' + str(fi) + '-' + str(_fi) + '/'
                tmp = (fi - 3) * 5 + _fi
                tmp = str(tmp)
                timeFileName = tmp + '-' + lowQOEName
                timePointList = getJsonFromFile(fullPath + timeFileName)
                # getUploadFeature
                uploadPackets = getJsonFromFile(fullPath + uploadName)
                # getDownloadFeature
                downloadPackets = getJsonFromFile(fullPath + downloadName)
                # getICMPFeature
                rttPackets = getJsonFromFile(fullPath + icmpName)
                badFeatureTable = []
                # get bad examples and good examples right after good examples
                goodFeatureTable = []
                FeatureTable = []
                yTable = []
                for i, timepoint in enumerate(timePointList):
                    flag = True
                    if (i + 1) < (len(timePointList) - 1):
                        goodTimepoint = timepoint + goodTimepointOffset + windowSize
                        if (goodTimepoint + windowSize) < timePointList[i + 1]:
                            goodFeatureList = getFeatureList(
                                goodTimepoint, uploadPackets, downloadPackets, rttPackets)
                            goodFeatureTable.append(goodFeatureList)
                            FeatureTable.append(goodFeatureList)
                            yTable.append(0)
                            flag = False
                            print 'good f table insert'
                            # print 'good feature:', goodFeatureList
                    if flag:
                        if len(goodFeatureTable) > 1:
                            fakegood = goodFeatureTable[0]
                            goodFeatureTable.append(fakegood)
                            FeatureTable.append(fakegood)
                            yTable.append(0)
                        else:
                            pass
                    badfeatureList = []
                    badfeatureList = getFeatureList(
                        timepoint, uploadPackets, downloadPackets, rttPackets)
                    # print 'bade Feature:', badfeatureList
                    print ' '
                    badFeatureTable.append(badfeatureList)
                    FeatureTable.append(badfeatureList)
                    yTable.append(1)
                    # print np.array(FeatureTable)
                    # print len(FeatureTable)
                print goodFeatureTable
                goodNP = np.array(goodFeatureTable)
                badNP = np.array(badFeatureTable)
                goodNP = goodNP.reshape(-1, 9)
                goodFeature = np.vstack((goodFeature, goodNP))
                badFeature = np.vstack((badFeature, badNP))
                FeatureNP = np.array(FeatureTable)
                x = np.vstack((x, FeatureNP))
                yNP = np.array(yTable)
                y = np.hstack((y, yNP))
    dataclass = data(x, y, goodFeature, badFeature)
    np.savetxt('feature.txt', dataclass.x_data)
    np.savetxt('y_target.txt', dataclass.y_target)
    np.savetxt('goodFeature.txt', dataclass.goodData)
    np.savetxt('badFeature.txt', dataclass.badData)
    return dataclass


def getFeatureList(timepoint, uploadPackets, downloadPackets, rttPackets):
    featureList = []
    PacketList = EF.ExtractPackge_func(
        uploadPackets, timepoint, windowSize)
    uF = getShareFeature(PacketList, windowSize)
    featureList = featureList + uF
    PacketList = EF.ExtractPackge_func(
        downloadPackets, timepoint, windowSize)
    dF = getShareFeature(PacketList, windowSize)
    featureList = featureList + dF
    PacketList = EF.ExtractPackge_func(
        rttPackets, timepoint, windowSize)
    RTT = EF.Avg_RTT_func(PacketList)
    featureList.append(RTT)
    return featureList


def getShareFeature(PacketList, windowSize):
    if len(PacketList) < 1:
        empty = [0.0, 0.0, 1.0, 0.0]
        return empty
    avg_thu = EF.Avg_Throughtput_func(PacketList, windowSize) / 100
    var_size = EF.Var_PacketSize_func(PacketList) / 100000.0
    avg_interval = float(EF.Avg_ArrivingInterval_func(
        PacketList, windowSize) * 100)
    var_time = float(EF.Var_ArrivingInterval_func(PacketList) * 10000)
    shareFeature = [avg_thu, var_size, avg_interval, var_time]
    return shareFeature


def getJsonFromFile(filePathStr):
    print filePathStr
    with open(filePathStr) as dataFile:
        try:
            data = json.load(dataFile)
            return data
        except Exception as e:
            print e
            dataFile.close
            removeLine(filePathStr, 2)
            return getJsonFromFile(filePathStr)
            # modify file and retry
        finally:
            pass
        dataFile.close


def removeLine(filename, lineno):
    f = os.open(filename, os.O_RDWR)
    m = mmap(f, 0)
    p = 0
    for i in range(lineno - 1):
        p = m.find('\n', p) + 1
    q = m.find('\n', p)
    m[p:q] = ' ' * (q - p)
    os.close(f)


getData()
