#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import subprocess
import time
from logger import *
from config import *
from functions import *

class liveThread(threading.Thread):
    def __init__(self, deviceid, rtmp, rtsp):
        threading.Thread.__init__(self)
        self.deviceid = deviceid 
        self.rtmp = rtmp
        self.cmd = 'avconv -rtsp_transport tcp -i "%s" -vcodec libx264 -f flv -r 15 -s 640x480 -an "rtmp://localhost:%d/live/camera-%d"' % (rtsp, RTMP_PORT, deviceid)

    def run(self):
        while True:
            self.requestPending()
            child = subprocess.Popen(self.cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            count = 0
            while True:
                #以读取到ffmpeg进程持续输出为标志
                time.sleep(1)
                rubbish = child.stderr.readline()
                count += 1
                if count == 10:
                    break
            self.requestStarted()
            child.wait()

    def requestPending(self):
        msg = "deviceid=%d&url=%s" % (self.deviceid, self.rtmp)
        sendRequest(msg, SERVER_IP, SERVER_PORT, live_pending_api, "POST")

    def requestStarted(self):
        msg = "deviceid=%d" % (self.deviceid)
        sendRequest(msg, SERVER_IP, SERVER_PORT, live_started_api, "POST")
