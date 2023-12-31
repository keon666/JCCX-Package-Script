#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import platform
import utils
import sys
import concurrent.futures as cf
from alive_progress import alive_bar
import subprocess
import shutil

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
packageRoot = os.path.split(scriptRoot)[0]
engineRoot = None
recordFile = os.path.join('..', 'record', 'encrypt_lua_record.jccx')
recordDic = {}
curRecordDic = {}

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
        if item[0] == '.':
            continue
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if os.path.isfile(nSrc):
            if isLuaFile(nSrc) and __isChange(nSrc):
                files.append((nSrc, nDest))
        else:
            if not os.path.exists(nDest):
                os.mkdir(nDest)
            getfiles(nSrc, nDest)

def __doFile(src, dest):
    dest2 = os.path.splitext(dest)[0] + '.luac'
    try:
        jitcmd = '%s -bg "%s" "%s"' %(jitPath, src, dest2)
        cmd = subprocess.Popen(jitcmd, shell = True, stdout = subprocess.PIPE, env = new_env)
        cmd.wait()
    except Exception as e:
        print(e)

    if not os.path.exists(dest2):
        shutil.copyfile(src, dest)

def __isChange(file):
    b = False
    md5 = utils.calcMD5(file)
    path = utils.adaptPath(file)
    pos = path.find('../src/')+3
    key = path[pos:]
    if recordDic.get(key):
        oldMd5 = recordDic[key]['md5']
        if oldMd5 != md5:
            b = True
    else:
        b = True
    curRecordDic[key] = {'md5':md5}
    return b

def run():
    with alive_bar(len(files)) as bar:
        with cf.ThreadPoolExecutor() as p:
            for src, dest in files:
                p.submit(__doFile, src, dest).add_done_callback(lambda func: bar())

if __name__ == '__main__':
    print('::::::::::一、开始处理脚本加密::::::::')
    engineRoot = utils.joinDir(scriptRoot, '..', '..')
    # print('scriptRoot=', scriptRoot)
    # print('packageRoot=', packageRoot)
    # print('engineRoot=', engineRoot)
    initJitPath('64')

    src = utils.joinDir(engineRoot, 'src')
    dest = utils.joinDir(packageRoot, 'assets', 'src')
    if not os.path.exists(dest):
        os.makedirs(dest)

    recordDic = utils.loadRecord(recordFile)
    getfiles(src, dest)
    run()
    utils.generateRecord(recordFile, curRecordDic)
    print('::::::::::开始处理脚本加密end::::::::')