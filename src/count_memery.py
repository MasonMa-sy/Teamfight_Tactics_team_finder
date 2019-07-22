#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:gbk
# https://www.cnblogs.com/zhbzz2007/p/5394782.html
import os, re
import time
import string

#统计某一个进程名所占用的内存，同一个进程名，可能有多个进程
def countProcessMemoey(processName):
    pattern = re.compile(r'([^\s]+)\s+(\d+)\s.*\s([^\s]+\sK)')
    cmd = 'tasklist /fi "imagename eq ' + processName + '"' + ' | findstr.exe ' + processName
    result = os.popen(cmd).read()
    resultList = result.split("\n")

    for srcLine in resultList:
        srcLine = "".join(srcLine.split('\n'))
        if len(srcLine) == 0:
            break
        m = pattern.search(srcLine)
        if m is None:
            continue
        # 由于是查看python进程所占内存，因此通过pid将本程序过滤掉
        if str(os.getpid()) == m.group(2):
            continue
        ori_mem = m.group(3).replace(',','')
        ori_mem = ori_mem.replace(' K','')
        ori_mem = ori_mem.replace(r'\sK','')
        memEach = int(ori_mem)
        print('ProcessName:' + m.group(1) + '\tPID:' + m.group(2) + '\tmemory size:%.2f'% (memEach * 1.0 /1024), 'M')

    print("*" * 58)


if __name__ == '__main__':
    # 进程名
    ProcessName = 'python.exe'

    while True:
        countProcessMemoey(ProcessName)
        time.sleep(5)
