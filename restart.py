#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
import os
import time
start_cmd = "python " + PROGRAM_ROOT + "start.py"
stop_cmd = "python " + PROGRAM_ROOT + "stop.py"
os.system(stop_cmd)
time.sleep(5)
os.system(start_cmd)