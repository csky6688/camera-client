#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from config import *
import os

app = web.application(urls, globals())

if __name__ == "__main__":
    pidfile = open(PIDFILE, "w")
    pidfile.write(str(os.getpid()))
    pidfile.close()
    app.run()
