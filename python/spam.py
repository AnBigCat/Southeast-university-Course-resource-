#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def spam1():
    print('还我血汗钱！')
    
def spam2(guy):
    print(guy + '你不是人！')
    
def spam3(guy):
    print(guy + '你还我血汗钱！')


'''
spam1()
spam1()
spam2('黄老板')
spam3('黄老板')
'''
#print(__name__)

if __name__ == '__main__':
    spam1()
    spam1()
    spam2('黄老板')
    spam3('黄老板')

    