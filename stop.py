#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from config import *

f = open(PIDFILE, "r")
pid = int(f.readline())
cmd = "kill %d" % pid 
os.system(cmd)