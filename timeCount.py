# -*- coding: utf-8 -*-
#from openpyxl import Workbook
import os
import re
def Get_date(cmd):
    servlet = os.popen(cmd)
    servletlines = servlet.readlines()
    servlet.close()
    datecount = {}
    phoneStatus0_flag = 0
    phoneStatus1_flag = 0
    UisConnectEvent_flag = 0
    for servletline in servletlines:
        if (phoneStatus0_flag == 0 and phoneStatus1_flag == 0 and UisConnectEvent_flag == 0):
            if re.match(r'.*phoneStatus:0.*', servletline):
                Statustime0 = servletline[11:23].strip()
                Statustime0 = Statustime0.replace(':','')
                Statustime0 = Statustime0.replace('.','').strip()
                phoneStatus0_flag = 1
        if (phoneStatus0_flag == 1 and phoneStatus1_flag == 0 and UisConnectEvent_flag == 0):
            if re.match(r'.*phoneStatus:1.*', servletline):
                Statustime1 = servletline[11:23].strip()
                Statustime1 = Statustime1.replace(':','')
                Statustime1 = Statustime1.replace('.','').strip()
                Ring_to_hungup_time = (int(Statustime1)-int(Statustime0))/1000
                phoneStatus1_flag = 1
        if (phoneStatus0_flag == 1 and phoneStatus1_flag == 1 and UisConnectEvent_flag == 0):
            if re.match(r'.*UisConnectEvent.*', servletline):
                Connenttime = servletline[11:23].strip()
                Connenttime = Connenttime.replace(':','')
                Connenttime = Connenttime.replace('.','').strip()
                Hungup_to_connent_time = (int(Connenttime)-int(Statustime1))/1000
                UisConnectEvent_flag = 1
        if (phoneStatus0_flag == 1 and phoneStatus1_flag == 1 and UisConnectEvent_flag == 1):
            re_time = re.compile(r'.*(time):(\w{10}).*')
            Callid = re_time.match(servletline).group(2)
            Ring_to_connent_time = (int(Connenttime)-int(Statustime0))/1000
            print ('The Callid is %s' % Callid)
            print ('The time from Ring(351-7) to hung up(357-0) is %.3f s' % Ring_to_hungup_time)
            print ('The time from Hung up(357-0) to connent(357-1) is %.3f s' % Hungup_to_connent_time)
            print ('The time from Ring(351-7) to connent(304) is %.3f s \n' % Ring_to_connent_time)
            UisConnectEvent_flag = 0
            phoneStatus0_flag = 0
            phoneStatus1_flag = 0
        #else:
        #    print('failed')    
    #按照key值（datetime）初始化datecount字典
        #if datetime not in datecount:
        #    datecount[datetime] = 0
        #count = datecount[datetime]
        #datecount[datetime] = count+1
    #SORTdatecount = sorted(datecount.items(),key=lambda item:item[0])
    #for key,value in SORTdatecount:
    #    print ('Time:%s Count:%s' % (key, value))
    #return SORTdatecount
    return
    #print (sorted(datecount.items(),key=lambda item:item[0]))

def Key_words_data(Keywordslist):
    data=[]
    for value in Keywordslist.values():
        Keyword_data = Get_date(value)
        data.append(Keyword_data)
    return data

def Save_excel(data,Keywordslist):
    wb = Workbook(write_only=True)
    ws=[]
    n = 0
    for key in Keywordslist.keys():
        ws = wb.create_sheet(title=key)
        ws.append(['time','count'])
        for i in data[n]:
            ws.append([i[0],i[1]])
        n = n+1
    save_path='keyword_count'
    save_path+='.xlsx'
    wb.save(save_path)
eventid357 = "grep \'workId(156,1)\' jtapiMessage.log.1 |grep -i -E \'UisAgentPhoneStatusNotifyEvent|uisconnectevent\'"
Get_date(eventid357)
#PollServlet = "grep \'PollServlet\' ccacs.log|awk -F \".\" \'{print $1}\'"
#ERROR = "grep \'ERROR\' ccacs.log|awk -F \".\" \'{print $1}\'"
#Error = "grep 'ERROR' ccacs.log"
#Keywordslist = {'eventid357': eventid357}
#data = Key_words_data(Keywordslist)
#Save_excel(data,Keywordslist)
