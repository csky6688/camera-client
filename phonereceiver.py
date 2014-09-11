#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import socket   #socket模块
import sys
from config import *

if __name__ == "__main__":
    deviceid = int(sys.argv[2])
    port = int(sys.argv[4])
    HOST = '0.0.0.0'
    PORT = port
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #定义socket类型，网络通信，TCP
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))   #套接字绑定的IP与端口
    s.listen(1)         #开始TCP监听
    count = 1
    while 1:
        filename = JPG_DIR + "%d-%06d.jpg" % (deviceid, count)
        f = open(filename, "w");
        conn,addr=s.accept()   #接受TCP连接，并返回新的套接字与IP地址
        while 1:
            data = conn.recv(2048)    #把接收的数据实例
            if len(data) ==0:   #如果输出结果长度为0，则告诉客户端完成。此用法针对于创建文件或目录，创建成功不会有输出信息
                break
            else:
                f.write(data); 
        f.close()
        newname = TEMP_DIR + "%d.jpg" % deviceid
        cmd = "mv %s %s" % (filename, newname)
        os.system(cmd)
        count += 1
    conn.close()     #关闭连接
