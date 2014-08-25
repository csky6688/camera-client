#!/usr/bin/env python
# coding: utf-8
import web
import logging

DB_HOST =       "localhost"
DB_NAME =       "cameraclient"
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
PIDFILE = "/Users/CH/Projects/camera-client/camera-client.pid"

MYSQL_CONNECT_CMD = "MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, charset = DB_CHARSET)"

