#encoding:utf-8
import re
import subprocess
import win32ui,win32process,win32api,win32com
import os

def find_by_port(port):
    code = os.system('netstat -ano | findstr "8118" ')
    if code == 0:
        print(True)
    else:
        print(False)

def find_through_subprocess():
    p = subprocess.Popen('wmic process where caption="Superplane.exe" get Handle', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    already_pids = re.findall('\d+',stdoutput.decode())
    for pid in already_pids:
        os.system('taskkill /pid {0} -t -F'.format(pid))
    a = 1


if __name__=="__main__":
    find_through_subprocess()
