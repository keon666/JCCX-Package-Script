#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import utils
import concurrent.futures as cf
from alive_progress import alive_bar
import subprocess

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
engineRoot = None
files = []
ffmpegPath = os.path.join('..', 'ffmpeg', 'bin', 'ffmpeg')
recordFile = os.path.join('..', 'record', 'convert_audio_record.jccx')
recordDic = {}
curRecordDic = {}

def getfiles(src, dest):
    for item in os.listdir(src):
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if os.path.isfile(nSrc):
            if __isChange(nSrc):
                files.append((nSrc, nDest))
        else:
            getfiles(nSrc, nDest)

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

def __convert(src, dest):
    dir = os.path.split(dest)[0]
    if not os.path.exists(dir):
        os.mkdir(dir)
    dest = os.path.splitext(dest)[0] + '.ogg'

    cmd_str = '%s -y -i %s -acodec libvorbis -ab 96k -loglevel quiet %s' %(ffmpegPath, src, dest)
    cmd = subprocess.Popen(cmd_str, shell = True, stdout = subprocess.PIPE)
    cmd.wait()

def run():
    with alive_bar(len(files)) as bar:
        with cf.ThreadPoolExecutor() as p:
            for src, dest in files:
                p.submit(__convert, src, dest).add_done_callback(lambda func: bar())

if __name__ == '__main__':
    print('::::::::::①开始处理音频转换::::::::')
    engineRoot = utils.joinDir(scriptRoot, '..', '..')
    # print('scriptRoot=', scriptRoot)
    # print('engineRoot=', engineRoot)

    src = utils.joinDir(engineRoot, 'res', 'audio', 'bgm')
    dest = utils.joinDir(scriptRoot, '..', 'assets', 'res', 'audio', 'bgm')
    if not os.path.exists(dest):
        os.makedirs(dest)

    recordDic = utils.loadRecord(recordFile)
    getfiles(src, dest)
    run()
    utils.generateRecord(recordFile, curRecordDic)
    print('::::::::::处理音频转换end::::::::')