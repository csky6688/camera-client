#!/usr/bin/env python
# coding: utf-8
import web
import logging
import MySQLdb

DB_HOST =       "localhost"
DB_NAME =       "camera-client"
DB_USER =       "root"
DB_PASSWORD =   "root"
DB_CHARSET =    "utf8"
site_prefix = ""


render = web.template.render('template/', globals={ 'str' : str}, cache = False)
web.config.debug = False

urls = (
    site_prefix + 'api',             'api.index',
)

logfile = "logs/client.log"
LOG_LEVEL = logging.DEBUG
PIDFILE = "/home/camera/camera-client/camera-client.pid"

MYSQL_CONNECT_CMD = "MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, charset = DB_CHARSET)"

SERVER_IP = "10.0.0.197"
SERVER_PORT = 8087
RTMP_PORT = 8085
FILE_PORT = 8084
RTMP_ROOT = "rtmp://" + SERVER_IP + ":" + str(RTMP_PORT)
FILE_ROOT = "http://" + SERVER_IP + ":" + str(FILE_PORT)

live_pending_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) +   "/api?method=livepending"
live_started_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) +   "/api?method=livestarted"
record_start_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) + "/api?method=recordstarted"