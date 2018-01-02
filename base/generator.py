# -*- coding: utf-8 -*-

def triangles():
    L=[1]
    m=0
    while True:
        yield L
        L =[L[x]+L[x+1] for x in range(m)]
        L.insert(0,1)
        L.append(1)
        m=m+1

n = 0
results = []
for t in triangles():
    print (t)
    results.append(t)
    print (results)
    n=n+1
    if n==10:
        break
print (results)
