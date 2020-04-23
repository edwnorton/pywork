#!/usr/local/python3/bin/python3
# -*- coding: UTF-8 -*-
from django.test import TestCase
import requests
from requests.auth import HTTPBasicAuth
import json
import os,sys
import django
from requests.packages.urllib3.exceptions import InsecureRequestWarning


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from networklink.models import *

vcenter_api_url = 'https://ip/rest'
api_user = ''
api_pass = ''

def auth_vcenter(username,password):
    print('Authenticating to vCenter, user: {}'.format(username))
    resp = requests.post('{}/com/vmware/cis/session'.format(vcenter_api_url),auth=(api_user,api_pass),verify=False)
    if resp.status_code != 200:
        print('11111111111111Error! API responded with: {}'.format(resp.status_code))
        return
    return resp.json()['value']


def get_vc_api_data(req_url):
    sid = auth_vcenter(api_user,api_pass)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #Disable SSL warnings
    resp = requests.get(req_url,verify=False,headers={'vmware-api-session-id':sid})
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp    


def get_vcenter_hostname(nameid):
    hostname = ''
    resp = get_vc_api_data('{}/vcenter/host'.format(vcenter_api_url))
    j = resp.json()
    for i in j['value']:
        if i['name'] == nameid:
            hostname = i['host']
            break
    print('vCenter hostname: {}'.format(hostname))
    return hostname


def get_vcenter_vm_list(nameid):
    hostname = get_vcenter_hostname(nameid)
    namelist = []
    vmNameIp = {}
    res = []
    if hostname != '':
        resp = get_vc_api_data('{}/vcenter/vm?filter.hosts={}'.format(vcenter_api_url, hostname))
        vmlist = resp.json()
        for i in range(len(vmlist['value'])):
            namelist.append(vmlist['value'][i]['name'])
        for j in namelist:
            a = j.split('_')
            if len(j.split('_')) > 1:
                vmNameIp['name'] = a[0]
                vmNameIp['ip'] = a[-1]    
                res.append(vmNameIp)
                vmNameIp = {}
    return res


def get_vcenter_host_relation():
    nutanix = ['','']
    vminfo = {}
    res = []
    for i in nutanix:
        req_ip = i  # 获取请求id的ip
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #Disable SSL warnings
        data = get_vcenter_vm_list(req_ip)
        for j in data:
            vminfo["nutanixip"] = i
            vminfo["vmname"] = j["name"]
            vminfo["vmip"] = j["ip"]
            res.append(vminfo)
            vminfo = {}
    return res


def insert_data():
    data = get_vcenter_host_relation()
    vminfolist = []
    for i in data:
        vminfolist.append(t_vminfo(vmip=i['vmip'], vmname=i['vmname'], nutanixip=i['nutanixip']))
    
    t_vminfo.objects.bulk_create(vminfolist)

if __name__ == "__main__":
    t_vminfo.objects.all().delete()
    insert_data()












