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
            FFMPEG_BIN, 
            '-rtsp_transport', 'tcp',
            '-i', rtsp,
            '-c', 'copy',
            '-map', '0:0',
            '-f', 'flv',
            '-an',
            'rtmp://127.0.0.1:' + str(RTMP_PORT) + '/live/camera-' + str(deviceid)
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
                #time.sleep(1)
                output = rubbish.readline()
                if "Metadata" in output:
                    self.requestStarted()
                    break
                if child.poll() != None:
                    break
            child.wait()
            #os.rename(logfile, logfile + '-' + str(child.pid))
            if livemap[self.deviceid] == "STOP":
                break
            time.sleep(5)

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
        self.rtsp = rtsp
        self.videopath = VIDEO_PATH + "tmp/" + str(deviceid)
        try:
            os.makedirs(self.videopath)
        except:
            pass

    def run(self):
        count = 0
        while True:
            count += 1
            now = int(time.time())
            #获取当前距离最近一个时间点的秒数
            duration = 0
            while (now % RECORD_INTERVAL) != 0:
                duration += 1
                now += 1
            duration += 10

            self.cmd = [
                FFMPEG_BIN, 
                '-rtsp_transport', 'tcp',
                '-i', self.rtsp,
                '-c', 'copy',
                '-map', '0:0',
                '-t', str(duration),
                #'-f', 'segment',
                #'-segment_time', str(RECORD_INTERVAL),
                #'-segment_atclocktime', '1',
                '-an',
                self.videopath + '/' + str(self.deviceid) + '-' + str(count) + '.mp4'
            ]
            self.requestPending()
            logfile = CAMERA_LOG + str(self.deviceid) + "-record.log"
            log = open(logfile, "w")
            child = subprocess.Popen(self.cmd, stdout = subprocess.PIPE, stderr = log)
            recordmap[self.deviceid] = child
            rubbish = open(logfile, "r")
            while True:
                #以读取到ffmpeg进程持续输出为标志
                #time.sleep(1)
                output = rubbish.readline()
                if "Metadata" in output:
                    self.requestStarted()
                    break
                if child.poll() != None:
                    break
            child.wait()
            #os.rename(logfile, logfile + '-' + str(child.pid))
            if recordmap[self.deviceid] == "STOP":
                break
            #time.sleep(5)

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
        self.running = True
        self.working = False

    def getfiles(self, rootdir):
        for lists in os.listdir(rootdir):
            path = os.path.join(rootdir, lists)
            if os.path.isdir(path):
                self.getfiles(path)
            else:
                self.files.append(path)

    def stop(self):
        self.running = False

    def runonce(self):
        try:
            self.files = []
            self.getfiles(self.tmpdirs)
            for everyone in self.files:
                deviceid = int(os.path.basename(everyone).split("-")[0])
                child = subprocess.Popen([FFPROBE_BIN, everyone], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                for x in child.stderr.readlines():
                    if "Duration" in x:
                        end = float(os.stat(everyone).st_ctime)
                        duration = x.split(" ")[3].split(",")[0]
                        h = float(duration.split(":")[0])
                        m = float(duration.split(":")[1])
                        s = float(duration.split(":")[2])
                        duration = float(h * 3600 + m * 60 + s) 

                        start = end - duration
                        filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(start)) + ".mp4"
                        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
                        end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end))
                        newname = VIDEO_PATH + str(deviceid) + "/" + str(filename)

                        #重新转换以获得正确的视频开始时间
                        avconv = subprocess.Popen([
                            FFMPEG_BIN, 
                            "-i", everyone,
                            "-c", "copy",
                            "-movflags", "faststart",
                            everyone + ".fix.mp4"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                        avconv.wait()
                        os.remove(everyone)
                        everyone = everyone + ".fix.mp4"

                        try:
                            os.makedirs(VIDEO_PATH + str(deviceid))
                        except Exception, e:
                            pass
                        os.rename(everyone, newname)
                        images = subprocess.Popen([
                            FFMPEG_BIN, 
                            "-i", newname,
                            "-vframes", "1",
                            "-f", "image2",
                            newname + ".jpg"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                        images.wait()
                        self.requestNewRecordReady(deviceid, duration, start, end, os.path.basename(filename))

        except Exception, e:
            logger.info(str(e))

    def run(self):
        while self.running == True:
            self.runonce()
            time.sleep(3)

    def requestNewRecordReady(self, deviceid, duration, start, end, filename):
        path = FILE_ROOT + str(deviceid) + "/"
        url =  path + str(filename)

        msg = "deviceid=%d&duration=%f&start='%s'&end='%s'&url='%s'" % (int(deviceid), float(duration), str(start), str(end), url)
        return sendRequest(msg, SERVER_IP, SERVER_PORT, record_file_ready_api, "POST")
