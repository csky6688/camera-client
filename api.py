#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import web
from logger import *
from functions import *
from threads import *
import subprocess

class index:
    def POST(self):
        try:
            method = str(web.input().method)
            if method == "add":
                deviceid = int(web.input().deviceid)
                rtsp = str(web.input().rtsp)
                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "INSERT INTO devices(deviceid, rtsp) VALUES (%d, '%s');" % (deviceid, rtsp)
                cursor.execute(cmd)
                db.close()

            elif method == "startlive":
                deviceid = int(web.input().deviceid)   
                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "SELECT rtsp FROM devices WHERE deviceid = '%s';" % deviceid
                cursor.execute(cmd)
                rtsp = cursor.fetchone()[0]
                db.close()

                rtmp = "rtmp://" + RTMP_ROOT + "/live/camera-" + str(deviceid)              
                livethread = liveThread(deviceid, rtmp, rtsp)
                livethread.start()
                
            elif method == "stoplive":
                deviceid = int(web.input().deviceid)      

            elif method == "delete":
                #TODO: Stop all threads
                deviceid = int(web.input().deviceid)       
                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "DELETE FROM devices WHERE deviceid = '%s';" % deviceid
                cursor.execute(cmd)
                db.close()    

            elif method == "modify":
                deviceid = int(web.input().deviceid)    
                rtsp = str(web.input().rtsp)      

                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "SELECT rtsp FROM devices WHERE deviceid = '%s';" % deviceid
                cursor.execute(cmd)
                oldrtsp = cursor.fetchone()[0]
                if rtsp != oldrtsp:
                    #TODO: Stop all now threads, and start new.
                    cmd = "UPDATE devices SET rtsp = '%s' WHERE deviceid = '%s';" % (rtsp, deviceid)
                    cursor.execute(cmd)
                db.close()   

            else:
                return "未提供的方法"
                
        except Exception, e:
            logger.info(str(e))
            return "接口格式不正确"