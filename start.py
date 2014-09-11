#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from config import *
cmd = "python " + PROGRAM_ROOT + "main.py " + str(LOCAL_PORT)
os.system(cmd)