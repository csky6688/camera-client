#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import time
from config import *
from logger import *
import httplib

def sendRequest(msg, host, port, url, method):
    headers = {
        'Host': str(host) + ":" + str(port),
        'Content-Length': "%d" % len(msg),
        'User-Agent': "ZLW Video Client",
    }
    httpClient = httplib.HTTPConnection(host, port)
    httpClient.request(method, url, msg, headers)
    response = httpClient.getresponse()

    data = response.read()  

    return data

class PhoneRecordPublisher:
    def __init__(self):
        self.tmpdirs = VIDEO_PATH + "phone/"

    def getfiles(self, rootdir):
        for lists in os.listdir(rootdir):
            path = os.path.join(rootdir, lists)
            if os.path.isdir(path):
                self.getfiles(path)
            else:
                self.files.append(path)

    def runonce(self):
        try:
            self.files = []
            self.getfiles(self.tmpdirs)
            for everyone in self.files:
                deviceid = int(os.path.basename(everyone).split(".")[0])
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
                            "-c", "libx264",
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

    def requestNewRecordReady(self, deviceid, duration, start, end, filename):
        path = FILE_ROOT + str(deviceid) + "/"
        url =  path + str(filename)

        msg = "deviceid=%d&duration=%f&start='%s'&end='%s'&url='%s'" % (int(deviceid), float(duration), str(start), str(end), url)
        return sendRequest(msg, SERVER_IP, SERVER_PORT, record_file_ready_api, "POST")
