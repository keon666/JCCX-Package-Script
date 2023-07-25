#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import utils
import shutil
import concurrent.futures as cf
from alive_progress import alive_bar

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
engineRoot = None
files = []
recordFile = os.path.join('..', 'record', 'encrypt_png_record.jccx')
recordDic = {}
curRecordDic = {}

def getfiles(src, dest):
    for item in os.listdir(src):
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if os.path.isfile(nSrc) and __isChange(nSrc):
            files.append((nSrc, nDest))
        else:
            if not os.path.exists(nDest):
                os.mkdir(nDest)
            getfiles(nSrc, nDest)

def __copyFile(src, dest):
    if utils.checkFileExt(src):
        inFp = open(src, 'rb')
        buff = inFp.read()
        inFp.close()

        try:
            buff = utils.encrypt(buff)
        except Exception as e:
            print(e)

        outFp = open(dest, 'wb')
        outFp.write(buff)
        outFp.close()
    else:
        shutil.copyfile(src, dest)

def __isChange(file):
    b = False
    md5 = utils.calcMD5(file)
    path = utils.adaptPath(file)
    pos = path.find('../res/')+3
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
                p.submit(__copyFile, src, dest).add_done_callback(lambda func: bar())

if __name__ == '__main__':
    print('::::::::::三、开始处理图片加密::::::::')
    engineRoot = utils.joinDir(scriptRoot, '..', '..')
    # print('scriptRoot=', scriptRoot)
    # print('engineRoot=', engineRoot)

    src = utils.joinDir(engineRoot, 'res')
    dest = utils.joinDir(scriptRoot, '..', 'assets', 'res')
    if not os.path.exists(dest):
        os.makedirs(dest)

    recordDic = utils.loadRecord(recordFile)
    arr = ['ccs', 'font', 'live2d', 'particle', 'spine', 'texture', 'video']
    for item in arr:
        src2 = utils.joinDir(src, item)
        dest2 = utils.joinDir(dest, item)
        if not os.path.exists(dest2):
            os.mkdir(dest2)
        getfiles(src2, dest2)
    run()
    utils.generateRecord(recordFile, curRecordDic)
    print('::::::::::处理图片加密end::::::::')
    
