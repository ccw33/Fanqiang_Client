# encoding:utf-8
import os
import re
import signal
import subprocess
import traceback

import requests
import time
import win32api

from Utils.log_utils import logger

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
}
proxy_filt_path = 'Privoxy/config.txt'
server = "119.29.134.163:10082"
# server = "127.0.0.1:5082"


def test_ok(ip_with_port_text, proxy_type='socks5'):
    '''
    测试是否能翻墙
    :return:(是否ok<Bool>,原因<String>)
    '''
    try:
        print('测试{0}'.format(ip_with_port_text))
        resp = requests.get('https://www.google.com/', headers=headers,
                            proxies={'http': proxy_type + (
                                'h' if proxy_type == 'socks5' else '') + '://' + ip_with_port_text,
                                     'https': proxy_type + (
                                         'h' if proxy_type == 'socks5' else '') + '://' + ip_with_port_text},
                            timeout=10)
        return True
    except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout or requests.exceptions.SSLError as e:  # request 访问错误
        print(e)
        return False
    except Exception as e:
        logger.error(traceback.format_exc())
        return False


def check_and_update_conf():
    '''
    检查配置文件并更新
    :return:
    '''
    try:
        # -------检查配置文件
        with open(proxy_filt_path, 'r+') as frw:
            text = frw.read()
            # 首先查看privoxy有没有配置，如果没有则配置(先给个假ip_port，后面再改)
            if not re.findall(r'forward-socks5 \/ \d+\.\d+\.\d+\.\d+\:\d+ \.\nlisten-address 0\.0\.0\.0:8118\n', text):
                new_text = "forward-socks5 / %s .\nlisten-address 0.0.0.0:8118\n%s" % ('1.1.1.1:8080', text)
                frw.write(new_text)
            # 查出配置的ip_port
            frw.seek(0)
            text = frw.read()
            find_res = re.findall(r'forward-socks5 \/ (\d+\.\d+\.\d+\.\d+\:\d+)', text)
            # 验证是否能用,如果不能用就更新配置(测试两次，连续两次不行才换)
            if not test_ok(find_res[0]) and not test_ok(find_res[0]):
                try:
                    resp = requests.get('http://{0}/get_ip_port'.format(server),
                                        params={'account': 'CK_test', 'password': 'CK_test'}, timeout=2)
                except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout or requests.exceptions.SSLError as e:  # request 访问错误
                    print(e)
                    logger.debug("连接不上服务器")
                    return
                except Exception as e:
                    logger.error(traceback.format_exc())
                    return
                new_text = text.replace(find_res[0], resp.content.decode())
                frw.seek(0)
                frw.write(new_text)
    except Exception:
        logger.error(traceback.format_exc())


def startPrivoxy():
    # 启动privoxy
    # 更改工作目录到Privoxy
    os.chdir(os.getcwd() + '\\Privoxy')
    # 启动
    win32api.ShellExecute(0, 'open', os.getcwd() + '\\privoxy.exe', '', '', 0)
    # 把工作目录更改回上一级
    os.chdir('..')

def close_all_but_this():
    '''
    关闭钱买开了的Superplane进程
    :return:
    '''
    p = subprocess.Popen('wmic process where caption="Superplane.exe" get Handle', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    (stdoutput, erroutput) = p.communicate()
    already_pids = re.findall('\d+', stdoutput.decode())
    for pid in already_pids[:-2]:# 随后两个是本进程
        os.system('taskkill /pid {0} -t -F'.format(pid))


if __name__ == "__main__":
    # 关闭旧的进程
    close_all_but_this()
    if not os.system('netstat -ano | findstr "8118" '):
        startPrivoxy()
    time.sleep(1)
    while True:
        try:
            # 检查Privoxy是否已经关闭，如果关闭了就开启（客户可能会手动关闭Privoxy）
            code = os.system('netstat -ano | findstr "8118" ')
            if not code == 0:
                startPrivoxy()
            check_and_update_conf()
        except Exception:
            try:
                requests.get('http://{0}/get_client_error'.format(server),
                             params={'account': 'CK_test', 'error': traceback.format_exc()})
            except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout or requests.exceptions.SSLError as e:  # request 访问错误
                print(e)
            except Exception as e:
                logger.error(traceback.format_exc())
                # os.kill(current_pid,signal.CTRL_C_EVENT)
        finally:
            time.sleep(60)

