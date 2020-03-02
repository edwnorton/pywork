#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import time, os
import re
import logging.handlers
from prometheus_client import Gauge
from prometheus_client import start_http_server
from subprocess import Popen, PIPE


#HTTP端口
PORT = 18000

#查询间隔
querytime = 15

#应用指标
APP_SEND_KBPS = Gauge('app_send_kbps', 'app send kbps')
APP_RECIVE_KBPS = Gauge('app_recive_kbps', 'app recive kbps')

#LOG模块相关
LOG_FILE = r'app_traffic.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8')
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('sms_remain')  # 获取名为sms_remain的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)

def get_pid():
    '''获取查询进程的pid'''
    re_file = re.compile(r'(.*jar)$') #预编译关键字表达式
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(BASE_DIR)
    for file in files:
        m = re_file.match(file)
        if m:
            keyName = m.groups(1)[0]
            break
        else:
            pass
    cmd = r"ps -ef|grep -v grep|grep {0}|awk '".format(keyName) + r"{print $2}'"
    a = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = a.communicate()
    if stdout:
        pidstr = str(stdout).strip("\\n'").split("'")
        pid = pidstr[1]
    else:
        pid = '0'
    return pid


def get_app_traffic():
    '''获取app实时发送与接收流量'''
    try:
        trafficData = []
        pid = get_pid()
        print ("pid is {}".format(pid))
        cmd = r"nethogs -c 2 -d 5 -t eth0 2>&1|awk '/\/{0}\//".format(pid) + r"{print $0}'"
        a = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = a.communicate()
        print (stdout)
        if stdout:
            cmdResult = str(stdout).strip("\\n'").split("\\t")
            trafficData = [float(cmdResult[1]), float(cmdResult[2])]
            print("stdout not kong {0}".format(trafficData))
        else:
            trafficData = [0, 0]
            print("stdout kong {0}".format(trafficData))
    except Exception as e:
        logger.error(e)
    return trafficData


def monitoring():
    '''埋点'''
    try:
        traffic = get_app_traffic()
        print(traffic)
        send, recive = traffic[0], traffic[1]
        logger.info('APP 实时发送与接收流量分别为:{0},{1}'.format(send, recive))
        APP_SEND_KBPS.set(send)
        APP_RECIVE_KBPS.set(recive)
    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    start_http_server(PORT)
    while True:
        monitoring()
        time.sleep(querytime)
