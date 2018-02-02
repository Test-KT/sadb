#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, unicode_literals #

import re  #正则表达式库
import subprocess  #用于执行外部命令和程序，比如shell或者cmd这些
import sys #系统相关操作库
import datetime
from distutils.spawn import find_executable  #用于查找shell命令是否存在
from pprint import pprint  #日志打印库

adb_path = find_executable("adb") #找出shell命令的路径，用于判断是否存在

if not adb_path:
    print('adb path not found.')
    exit(-1)

if sys.version_info.major == 2:  #猜测是用于兼容不同Python版本
    input = raw_input


def sadb():
    devices, outputs = read_devices()
    args = read_args()  #读取参数类似 python xx.py 参数 参数 参数 
    device_count = len(devices)
    if len(args) == 0:  #没有找到设备
        print('just use sadb as an alias for adb')
        exit(-1) 
    if args[0] == 'devices':
        cmd = [adb_path]
        cmd += args
        subprocess.call(cmd) #执行命令，接收的参数是一个列表call(["ls", "-l"])
        exit(0)

    if device_count > 1: 
        nums = select_devices(devices)
        for seq in nums:
            exec_adb_cmd_on_device(devices[seq], args)#seq下标的设备对象
    elif device_count == 1:
        exec_adb_cmd_on_device(devices[0], args)
    else:
        print("No device found")
        exit(-1)


def select_devices(devices):
    """ 选择设备 """
    device_count = len(devices)
    print("Device list:")
    print("0) All devices")
    for i, d in enumerate(devices, start=1):
        print("%d) %s\t%s" % (i, d['serial'], d['model']))
    print("q) Exit this operation")
    selected = input("\nselect: ")
    if selected == '0':
        nums = range(0, device_count)
    elif selected == 'q':
        print("Exit this operation")
        exit(-1)
    else:
        nums = []
        for i in re.split(r'[\s+,]', selected): #分割多个输入
            if i.isdigit(): #检测字符串是否只由数字组成
                seq = int(i) - 1
                if 0 <= seq < device_count:
                    nums.append(seq)
                    continue
            print("error input: %s, retry again\n" % i) 
            return select_devices(devices)
    return nums


def read_args():
    """ 读取参数 """
    return sys.argv[1:]


def read_devices():
    """ 读取设备列表 """
    devices = [] #存放设备信息数据
    outputs = [] #存放没有处理的设备数据
    proc = subprocess.Popen([adb_path, 'devices', '-l'], stdout=subprocess.PIPE) #重定向输出，类似shell中的 ls > 2.txt
    while True:
        line = proc.stdout.readline().decode('utf-8').strip() #分行读取并清除前后空格
        outputs.append(line)
        if not line:
            break
        if line.strip() and not line.startswith('List of devices'):
            d = re.split(r'\s+', line.strip())#正则分割数据\s表示空格
            # print("serial: %s, model: %s, transport_id: %s\n" % (d[0],d[4],d[6]))
            devices.append({
                'serial': d[0],
                'usb': d[2],
                'product': d[3],
                'model': d[4],
                'device': d[5]
            })

    return devices, outputs


def exec_adb_cmd_on_device(device, args):
    """ 执行 adb 命令 """
    cmd = [adb_path, "-s", device['serial']] #组装adb命令
    cmd += args #添加上参数
    now=datetime.datetime.now()
    print('\n[{timedate}] [{model}]exec: adb -s {serial} {cmd}'.format(cmd=' '.join(args), serial=device['serial'], model=device['model'],timedate=now.strftime("%Y-%m-%d %H:%M:%S")))
    subprocess.call(cmd)


def dd(obj):
    """ just for debug. """
    print(obj)
    exit(0)
