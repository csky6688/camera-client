#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import web
from logger import *
from functions import *
from threads import *
from config import *

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

                rtmp = RTMP_ROOT + "/live/camera-" + str(deviceid)              
                livethread = liveThread(deviceid, rtmp, rtsp)
                livethread.start()
                
            elif method == "stoplive":
                deviceid = int(web.input().deviceid) 
                child = livemap[deviceid]
                livemap[deviceid] = "STOP"
                child.kill()

            elif method == "startrecord":
                deviceid = int(web.input().deviceid)    
                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "SELECT rtsp FROM devices WHERE deviceid = '%s';" % deviceid
                cursor.execute(cmd)
                rtsp = cursor.fetchone()[0]
                db.close()
       
                recordthread = recordThread(deviceid, rtsp)
                recordthread.start()

                filethread = saveRecordFileThread()
                filethread.start()

            elif method == "stoprecord":
                deviceid = int(web.input().deviceid)      
                child = recordmap[deviceid]
                recordmap[deviceid] = "STOP"
                child.terminate()


            elif method == "delete":
                deviceid = int(web.input().deviceid)       
                db = eval(MYSQL_CONNECT_CMD)
                cursor = db.cursor()
                cmd = "DELETE FROM devices WHERE deviceid = '%s';" % deviceid
                cursor.execute(cmd)
                db.close()    

            else:
                return "未提供的方法"
                
        except Exception, e:
            logger.info(str(e))
            return "接口格式不正确"