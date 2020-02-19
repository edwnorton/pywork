import xlrd
import json
import os
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
excfile = "./111.xlsx"
jsfile = "./Vm.json"
cols = []
with open(jsfile, 'r',encoding='utf8') as fp:
    line = fp.readline()
line1 = eval(line)
for key,value in line1.items():
    data = value
    for k in value[0].keys():
        if k not in cols:
            cols.append(k)
    ws.append(cols)
for v in data:
    rowdata = []
    for col in cols:
        rowdata.append(v.get(col))
    ws.append(rowdata)
wb.save(excfile)
