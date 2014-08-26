#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import subprocess
import time
import os
from logger import *
from config import *
from functions import *

class liveThread(threading.Thread):
    def __init__(self, deviceid, rtmp, rtsp):
        threading.Thread.__init__(self)
        self.deviceid = deviceid 
        self.rtmp = rtmp
        self.cmd = [
            'avconv', 
            '-rtsp_transport', 'tcp',
            '-i', rtsp,
            '-c', 'copy',
            '-map', '0:0',
            '-f', 'flv',
            '-an',
            'rtmp://localhost:' + str(RTMP_PORT) + '/live/camera-' + str(deviceid)
        ]

    def run(self):
        while True:
            self.requestPending()
            logfile = CAMERA_LOG + str(self.deviceid) + "-live.log"
            log = open(logfile, "w")
            child = subprocess.Popen(self.cmd, stdout = log, stderr = log)
            livemap[self.deviceid] = child
            rubbish = open(logfile, "r")
            while True:
                #以读取到ffmpeg进程持续输出为标志
                time.sleep(1)
                output = rubbish.readline()
                if "RTSP/RTP stream from IPNC" in output:
                    break
            self.requestStarted()
            child.wait()
            if livemap[self.deviceid] == "STOP":
                break

    def requestPending(self):
        msg = "deviceid=%d&url=%s" % (self.deviceid, self.rtmp)
        sendRequest(msg, SERVER_IP, SERVER_PORT, live_pending_api, "POST")

    def requestStarted(self):
        msg = "deviceid=%d" % (self.deviceid)
        sendRequest(msg, SERVER_IP, SERVER_PORT, live_started_api, "POST")


class recordThread(threading.Thread):
    def __init__(self, deviceid, rtsp):
        threading.Thread.__init__(self)
        self.deviceid = deviceid 
        videopath = VIDEO_PATH + "tmp/" + str(deviceid)
        try:
            os.makedirs(videopath)
        except:
            pass
        self.cmd = [
            'avconv', 
            '-rtsp_transport', 'tcp',
            '-i', rtsp,
            '-c', 'copy',
            '-map', '0:0',
            '-f', 'segment',
            '-segment_time', str(RECORD_INTERVAL),
            videopath + '/' + str(deviceid) + '-%02d.mp4'
        ]

    def run(self):
        while True:
            self.requestPending()
            logfile = CAMERA_LOG + str(self.deviceid) + "-record.log"
            log = open(logfile, "w")
            child = subprocess.Popen(self.cmd, stdout = subprocess.PIPE, stderr = log)
            recordmap[self.deviceid] = child
            rubbish = open(logfile, "r")
            while True:
                #以读取到ffmpeg进程持续输出为标志
                time.sleep(1)
                output = rubbish.readline()
                if "RTSP/RTP stream from IPNC" in output:
                    break
            self.requestStarted()
            child.wait()
            if recordmap[self.deviceid] == "STOP":
                break

    def requestPending(self):
        msg = "deviceid=%d" % (self.deviceid)
        sendRequest(msg, SERVER_IP, SERVER_PORT, record_pending_api, "POST")

    def requestStarted(self):
        msg = "deviceid=%d" % (self.deviceid)
        sendRequest(msg, SERVER_IP, SERVER_PORT, record_started_api, "POST")

class saveRecordFileThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tmpdirs = VIDEO_PATH + "tmp/"

    def getfiles(self, rootdir):
        for lists in os.listdir(rootdir):
            path = os.path.join(rootdir, lists)
            if os.path.isdir(path):
                self.getfiles(path)
            else:
                self.files.append(path)

    def run(self):
        while True:
            try:
                self.files = []
                self.getfiles(self.tmpdirs)
                for everyone in self.files:
                    deviceid = int(os.path.basename(everyone).split("-")[0])
                    child = subprocess.Popen(["avprobe", everyone], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    for x in child.stderr.readlines():
                        if "Duration" in x:
                            faststart = subprocess.Popen(["qt-faststart", everyone, everyone + ".new"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                            faststart.wait()
                            os.remove(everyone)
                            everyone = everyone + ".new"
                            duration = x.split(" ")[3].split(",")[0]
                            h = float(duration.split(":")[0])
                            m = float(duration.split(":")[1])
                            s = float(duration.split(":")[2])
                            duration = h * 3600 + m * 60 + s 
                            end = float(os.stat(everyone).st_ctime)
                            start = end - duration
                            filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(start)) + ".mp4"
                            start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
                            end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end))

                            newname = VIDEO_PATH + str(deviceid) + "/" + str(filename)
                            
                            try:
                                os.makedirs(VIDEO_PATH + str(deviceid))
                            except Exception, e:
                                pass
                            os.rename(everyone, newname)
                            self.requestNewRecord(deviceid, duration, start, end, os.path.basename(filename))

                time.sleep(10)

            except Exception, e:
                print  str(e)

    def requestNewRecord(self, deviceid, duration, start, end, filename):
        path = FILE_ROOT + str(deviceid) + "/"
        url =  path + str(filename)

        msg = "deviceid=%d&duration=%f&start='%s'&end='%s'&url='%s'" % (int(deviceid), float(duration), str(start), str(end), url)
        sendRequest(msg, SERVER_IP, SERVER_PORT, record_add_api, "POST")