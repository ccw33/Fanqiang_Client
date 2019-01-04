#encoding:utf-8
import win32ui,win32process,win32api,win32com
import os
# 通过端口查看进程
code = os.system('netstat -ano | findstr "8118" ')
if code == 0:
    print(True)
else:
    print(False)