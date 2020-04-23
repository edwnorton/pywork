#!/usr/local/python3/bin/python3
# -*- coding: UTF-8 -*-
import time, os
import datetime
import re
import logging.handlers
import hashlib
import threading
from prometheus_client import Gauge
from prometheus_client import start_http_server
from subprocess import Popen, PIPE


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rman_bak_dir = os.path.join(BASE_DIR, 'rman_bak')
expdp_bak_dir = os.path.join(BASE_DIR, 'expdp_bak')
md5sum_rman_file = os.path.join(rman_bak_dir,'md5sum')
md5sum_expdp_file = os.path.join(expdp_bak_dir,'md5sum')

#HTTP端口
PORT = 18000


#应用指标
RMAN_BAK_RES = Gauge('rman_bak_res', 'rman bak res')
EXPDP_BAK_RES = Gauge('expdp_bak_res', 'expdp bak res')

#LOG模块相关
LOG_FILE = r'bak_file_monitor.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8')
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('sms_remain')  # 获取名为sms_remain的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)



def md5sum(filename):
    try:
        md5_value = hashlib.md5()
        with open(filename, 'rb') as f:
            while True:
                data = f.read(8096)
                if not data:
                    break
                md5_value.update(data)
    except Exception as e:
        logger.error(e)
    return md5_value.hexdigest()


def get_bak_result():
    '''获取备份结果'''
    res = {}
    dt = datetime.datetime.now()
    dst = dt.strftime('%Y%m%d')
    #re_file = re.compile(r'(ora_bak_all_{0}.tar.gz)$'.format(dst)) #预编译关键字表达式
    rman_bak_file = os.path.join(rman_bak_dir,'ora_rman_bak_all_{0}.tar.gz'.format(dst))
    expdp_bak_file = os.path.join(expdp_bak_dir,'ora_expdp_bak_all_{0}.tar.gz'.format(dst))
    if os.path.exists(rman_bak_file):
        with open(md5sum_rman_file) as f:
            line = f.readline()
            src_rman_md5 = line.strip()
        dis_rman_md5 = md5sum(rman_bak_file)
        if src_rman_md5 == dis_rman_md5:
            res['rman'] = [0, 'success']
        else:
            res['rman'] = [1, 'md5校验失败']
    else:
        res['rman'] = [2, 'rman备份文件未生成']

    if os.path.exists(expdp_bak_file):
        with open(md5sum_expdp_file) as f:
            line = f.readline()
            src_expdp_md5 = line.strip()
        dis_expdp_md5 = md5sum(expdp_bak_file)
        if src_expdp_md5 == dis_expdp_md5:
            res['expdp'] = [0, 'success']
        else:
            res['expdp'] = [1, 'md5校验失败']
    else:
        res['expdp'] = [2, 'expdp备份文件未生成']
    return res



def monitoring():
    '''埋点'''
    try:
        #timer = threading.Timer(86400,monitoring)
        timer = threading.Timer(86400,monitoring)
        timer.start()
        bak_result = get_bak_result()
        if bak_result['rman'][0] == 0:
            logger.info('rman备份文件成功:{0}'.format(bak_result))
            RMAN_BAK_RES.set(1)
        else:
            logger.error(bak_result['rman'])
            RMAN_BAK_RES.set(0)

        if bak_result['expdp'][0] == 0:
            logger.info('expdp备份文件成功:{0}'.format(bak_result))
            EXPDP_BAK_RES.set(1)
        else:
            logger.error(bak_result['expdp'])
            EXPDP_BAK_RES.set(0)
    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    start_http_server(PORT)
    dt = datetime.datetime.now()
    dst_s = dt.strftime('%H:%M:%S')
    if dst_s > "00:10:00":
        monitoring()
