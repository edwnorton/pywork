#!/usr/local/python3/bin/python3
# -*- coding: UTF-8 -*-
import requests
import time
import os
import logging.handlers
import cx_Oracle
from subprocess import Popen, PIPE
from prometheus_client import Gauge
from prometheus_client import start_http_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#初始化oracle连接
cx_Oracle.init_oracle_client(config_dir="/home/oracle/product/11.2.0/db_1/network/admin")
connection = cx_Oracle.connect("common","common", "DEVDB", encoding="UTF-8")

#HTTP端口
PORT = 18000

#ora指标
ORA_MONITOR = Gauge('ora_monitor', 'ora_monitor,1为正常，0为异常')

ORACLE_SID = "devdb"

#oracle运行状态
ora_pmon_cmd = r'ps -ef | grep -w "ora_pmon_{0}" | grep -v grep'.format(ORACLE_SID)
ora_lsn_cmd = r'lsnrctl status|grep TNS-12541'
ora_lsn_start_cmd = r'lsnrctl start'


#LOG模块相关
LOG_FILE = r'oramonitor.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8')
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('oramonitor')  # 获取名为sms_remain的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)


def get_hostname():
    # 获取主机名
    hostname_cmd = os.popen('hostname')
    a = hostname_cmd.read().strip('\n')
    hostname_cmd.close()
    return a


def ora_check():
    # 检查ora实例状态
    try:
        orastartsh = os.path.join(BASE_DIR, 'orastart.sh')
        orastartsh_cmd = r'sh {0}'.format(orastartsh)
        ora_status = Popen(ora_pmon_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = ora_status.communicate()
        out = stdout.decode('utf-8')
        if out != "":
            lsn_status = Popen(ora_lsn_cmd, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = lsn_status.communicate()
            lsn_out = stdout.decode('utf-8')
            if lsn_out == "":
                ora_status_num = 1
                row = connection.version
                logger.info('oracle is running,{0}'.format(row))
                return ora_status_num
            else:
                ora_status_num = 0
                lsn_start = Popen(ora_lsn_start_cmd, stdout=PIPE, stderr=PIPE, shell=True)
                stdout, stderr = lsn_start.communicate()
                lsn_start_out = stdout.decode('utf-8')
                logger.info('oracle LISTENER has started')
                return ora_status_num
                
        else:
            ora_status_num = 0
            logger.info("oracle is down. Ready to start...")
            # 开始执行启动oracle脚本
            orastart_exec = Popen(orastartsh_cmd, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = orastart_exec.communicate()
            orastart_out = stdout.decode('utf-8')
            logger.info("oracle has started.Please check it {0}".format(orastart_out))
            return ora_status_num
    except Exception as e:
        logger.error(e)


def monitoring():
    '''埋点'''
    num = ora_check()
    ORA_MONITOR.set(num)
    return num


if __name__ == '__main__':
    start_http_server(PORT)
    while True:
        a = monitoring()
        if a == 1:
            time.sleep(30)
            continue
        else:
            break
