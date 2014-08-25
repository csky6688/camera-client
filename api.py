#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import web
from logger import *

class index:
    def POST(self):
        try:
            method = web.input().method
            print web.input()
            if method == "add":
                deviceid = int(web.input().deviceid)
                rtsp = str(web.input().rtsp)
                
            else:
                return "未提供的方法"
        except Exception, e:
            logger.info(str(e))
            return "接口格式不正确"