# -*- coding: utf-8 -*-
def recursive(n,a,b,c):
    if n==1:
        print(a,"-->",c)
    else:
        recursive(n-1,a,c,b)
        print(a,"-->",c)
        recursive(n-1,b,a,c)
if __name__=="__main__":
    recursive(4,"A","B","C")
