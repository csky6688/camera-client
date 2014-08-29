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

FFMPEG_BIN = "/home/camera/ffmpeg-2.3.3/ffmpeg"
FFPROBE_BIN = "/home/camera/ffmpeg/ffprobe"
PROGRAM_ROOT = "/home/camera/camera-client/"
CAMERA_LOG = PROGRAM_ROOT + "logs/"
logfile = PROGRAM_ROOT + "logs/client.log"
LOG_LEVEL = logging.DEBUG
PIDFILE = PROGRAM_ROOT + "camera-client.pid"
VIDEO_PATH = "/home/camera/www/videos/"

MYSQL_CONNECT_CMD = "MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, charset = DB_CHARSET)"

RECORD_INTERVAL = 3600     
SERVER_IP = "127.0.0.1"
LOCAL_IP = "121.49.97.4"
SERVER_PORT = 8087
LOCAL_PORT = 8086
RTMP_PORT = 8085
FILE_PORT = 8084
RTMP_ROOT = "rtmp://" + LOCAL_IP + ":" + str(RTMP_PORT)
FILE_ROOT = "http://" + LOCAL_IP + ":" + str(FILE_PORT) + "/videos/"

live_pending_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) +   "/api?method=livepending"
live_started_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) +   "/api?method=livestarted"
live_stop_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) +   "/api?method=livestop"
record_pending_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) + "/api?method=recordpending"
record_started_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) + "/api?method=recordstarted"
record_stop_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) + "/api?method=recordstop"
record_file_ready_api = "http://" +SERVER_IP + ":" + str(SERVER_PORT) + "/api?method=recordfileready"

livemap = {}
recordmap = {}

globalthreads = []
