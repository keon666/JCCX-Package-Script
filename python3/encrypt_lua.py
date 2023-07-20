#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import platform
import utils
import sys
import concurrent.futures as cf
from alive_progress import alive_bar
import subprocess

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
packageRoot = os.path.split(scriptRoot)[0]
engineRoot = os.path.split(packageRoot)[0]

jitPath = ""
new_env = os.environ.copy()

files = []

def initJitPath(mode):
    global jitPath
    global new_env
    sysstr = platform.system()
    if(sysstr =="Windows"):
        if "32" == mode:
            jitPath = utils.joinDir(packageRoot, "win32", "luajit.exe")
        else:
            jitPath = utils.joinDir(packageRoot, "win32", "64", "luajit.exe")
    elif(sysstr == "Linux"):
        jitPath = utils.joinDir(packageRoot, "linux", "luajit")
        if "64" == mode:
            jitPath = jitPath + "64"
    elif(sysstr == "Darwin"):
        jitPath = utils.joinDir(packageRoot, "mac", "luajit")
        if "64" == mode:
            jitPath = jitPath + "64"
    else:
        print("Unsupport OS!")
        sys.exit(-1)

    # important, to find luajit lua
    new_env['LUA_PATH'] = utils.joinDir(packageRoot, "?.lua")

def isLuaFile(file):
    ext = os.path.splitext(file)[1]
    if ext == '.lua':
        return True
    return False

def getfiles(src, dest):
    for item in os.listdir(src):
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if os.path.isfile(nSrc) and isLuaFile(nSrc):
            files.append((nSrc, nDest))
        else:
            getfiles(nSrc, nDest)

def __doFile(src, dest):
    dir = os.path.split(dest)[0]
    if not os.path.exists(dir):
        os.mkdir(dir)

    dest2 = os.path.splitext(dest)[0] + '.luac'
    jitcmd = '%s -bg "%s" "%s"' %(jitPath, src, dest2)
    cmd = subprocess.Popen(jitcmd, shell = True, stdout = subprocess.PIPE, env = new_env)
    cmd.wait()

def run():
    with alive_bar(len(files)) as bar:
        with cf.ThreadPoolExecutor() as p:
            for src, dest in files:
                p.submit(__doFile, src, dest).add_done_callback(lambda func: bar())

if __name__ == '__main__':
    print('::::::::::开始处理脚本加密::::::::')
    print('scriptRoot=', scriptRoot)
    print('packageRoot=', packageRoot)
    print('engineRoot=', engineRoot)
    initJitPath('64')

    src = utils.joinDir(engineRoot, 'src', 'app', 'login')
    dest = utils.joinDir(packageRoot, 'luac')
    if not os.path.exists(dest):
        os.mkdir(dest)

    print('=======获取lua文件=========')
    getfiles(src, dest)
    print('==========开始加密=========')
    run()
    print('=======加密完成!!!=========')