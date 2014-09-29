#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import time
from config import *
from functions import *

class RecordCleaner:
    def __init__(self):
        self.devicesinfo = {}
        self.devices = {}
    
    def run(self):
        self.getDevicesInfo()
        self.getRecords()
        self.getToDeleteFiles()
        self.doDelete()

    def getDevicesInfo(self):
        devices = eval(sendRequest("", SERVER_IP, SERVER_PORT, get_devices_info_api, "POST"))
        for everyone in devices:
            self.devicesinfo[everyone['id']] = everyone

    def getRecords(self):
        db = eval(MYSQL_CONNECT_CMD)
        cursor = db.cursor()
        cmd = "SELECT deviceid FROM devices";
        cursor.execute(cmd)
        deviceids = cursor.fetchall()
        for everyone in deviceids:
            deviceid = int(everyone[0]) 
            self.devices[deviceid] = {}
            path = VIDEO_PATH + str(deviceid)
            files = []
            try:
                self.getfiles(path, files) 
            except:
                pass
            try:
                keep = self.devicesinfo[deviceid]['keep']
            except:
                keep = 7
            
            self.devices[deviceid]['files'] = files 
            self.devices[deviceid]['keep'] = keep
        db.close()

    def getToDeleteFiles(self):
        for key in self.devices:
            keep = self.devices[key]['keep'] * 86400
            self.devices[key]['delete'] = []
            for everyone in self.devices[key]['files']:
                now = time.time()
                ctime = os.stat(everyone).st_ctime 
                if (now - ctime) > keep:
                    self.devices[key]['delete'].append(everyone)
    
    def doDelete(self):
        filenames = []
        for key in self.devices:
            for file in self.devices[key]['delete']:
                os.remove(file)
                basename = os.path.basename(file)
                filename = str(key) + "/" + basename
                filenames.append(filename)
        msg = "filenames=%s" % str(filenames)
        sendRequest(msg, SERVER_IP, SERVER_PORT, delete_records_api, "POST")

    def getfiles(self, rootdir, files):
        for lists in os.listdir(rootdir):
            path = os.path.join(rootdir, lists)
            if os.path.isdir(path):
                self.getfiles(path, files)
            else:
                files.append(path)


if __name__ == "__main__":
    cleaner = RecordCleaner()
    cleaner.run()