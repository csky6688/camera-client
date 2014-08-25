#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from logger import *
import httplib

def sendRequest(msg, host, port, url, method):
    headers = {
        'Host': str(host) + ":" + str(port),
        'Content-Length': "%d" % len(msg),
        'User-Agent': "ZLW Video Client",
    }
    httpClient = httplib.HTTPConnection(host, port)
    httpClient.request(method, url, msg, headers)
    response = httpClient.getresponse()

    data = response.read()  

    return data