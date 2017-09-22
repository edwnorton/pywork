# -*- coding: utf-8 -*-
from openpyxl import Workbook
import os
def Get_date(cmd):
    servlet = os.popen(cmd)
    servletlines = servlet.readlines()
    servlet.close()
    datecount = {}
    for servletline in servletlines:
        datetime = servletline[8:13].strip()
        datetime = datetime.replace(' ','-')
    #按照key值（datetime）初始化datecount字典
        if datetime not in datecount:
            datecount[datetime] = 0
        count = datecount[datetime]
        datecount[datetime] = count+1
    SORTdatecount = sorted(datecount.items(),key=lambda item:item[0])
    for key,value in SORTdatecount:
        print ('Time:%s Count:%s' % (key, value))
    return SORTdatecount
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
#PollServlet = "grep 'PollServlet' ccacs.log"
PollServlet = "grep \'PollServlet\' ccacs.log|awk -F \".\" \'{print $1}\'"
ERROR = "grep \'ERROR\' ccacs.log|awk -F \".\" \'{print $1}\'"
#Error = "grep 'ERROR' ccacs.log"
Keywordslist = {'PollServlet': PollServlet, 'ERROR': ERROR}
data = Key_words_data(Keywordslist)
Save_excel(data,Keywordslist)
