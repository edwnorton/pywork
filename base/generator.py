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
if results == [
    [1],
    [1, 1],
    [1, 2, 1],
    [1, 3, 3, 1],
    [1, 4, 6, 4, 1],
    [1, 5, 10, 10, 5, 1],
    [1, 6, 15, 20, 15, 6, 1],
    [1, 7, 21, 35, 35, 21, 7, 1],
    [1, 8, 28, 56, 70, 56, 28, 8, 1],
    [1, 9, 36, 84, 126, 126, 84, 36, 9, 1]
]:
    print('????!')
else:
    print('????!')
