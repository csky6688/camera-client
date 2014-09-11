#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from functions import *
from logger import *
from config import *
import os
import sys
import signal
import time
from threads import *

app = web.application(urls, globals())

def exit_handler(signal, frame):
    #捕获SIGTERM信号
    for everyone in livemap:
        child = livemap[everyone]
        try:
            livemap[everyone] = "STOP"
            child.terminate()
        except Exception, e:
            print str(e)
        msg = "deviceid=%d" % int(everyone)
        sendRequest(msg, SERVER_IP, SERVER_PORT, live_stop_api, "POST")

    for everyone in recordmap:
        child = recordmap[everyone]
        try:
            recordmap[everyone] = "STOP"
            child.terminate()
        except Exception, e:
            print str(e)
        msg = "deviceid=%d" % int(everyone)
        sendRequest(msg, SERVER_IP, SERVER_PORT, record_stop_api, "POST")

    for everyone in socketmap:
        child = socketmap[everyone]
        try:
            socketmap[everyone] = "STOP"
            child.kill()
        except Exception, e:
            print str(e)

    for everyone in phonelivemap:
        child = phonelivemap[everyone]
        try:
            phonelivemap[everyone] = "STOP"
            child.terminate()
        except Exception, e:
            print str(e)

    for everyone in phonerecordmap:
        child = phonerecordmap[everyone]
        try:
            phonerecordmap[everyone] = "STOP"
            child.terminate()
        except Exception, e:
            print str(e)

    thread = globalthreads[0]
    thread.running = False
    thread.join()
    thread.runonce()
    PhoneRecordPublisher().runonce()
    #随后无条件杀死
    f = open(PIDFILE, "r")
    pid = int(f.readline())
    cmd = "kill -9 %d" % pid
    os.system(cmd)

def daemonize(stdin = '/dev/null', stdout = '/dev/null', stderr = '/dev/null'): 
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
    
    os.chdir(PROGRAM_ROOT) 
    os.umask(0) 
    os.setsid() 
     
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
         
    for f in sys.stdout, sys.stderr: 
        f.flush() 
     
    si = file(stdin, 'r') 
    so = file(stdout, 'a+') 
    se = file(stderr, 'a+', 0) 
    os.dup2(si.fileno(), sys.stdin.fileno()) 
    os.dup2(so.fileno(), sys.stdout.fileno()) 
    os.dup2(se.fileno(), sys.stderr.fileno())

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, exit_handler)
    daemonize(stdout = PROGRAM_ROOT + 'sys.log', stderr = PROGRAM_ROOT + 'sys.err') 
    pidfile = open(PIDFILE, "w")
    pidfile.write(str(os.getpid()))
    pidfile.close()
    recordfilethread = saveRecordFileThread()
    globalthreads.append(recordfilethread)
    recordfilethread.start()
    PhoneRecordPublisher().runonce()
    app.run()
