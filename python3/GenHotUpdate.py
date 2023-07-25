#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import hashlib
import subprocess
import sys
import shutil
import utils
import concurrent.futures as cf
from alive_progress import alive_bar

CUR_VERIOSN = '1.0.0'
COPY_DIFF = False
if len(sys.argv) == 2:
    CUR_VERIOSN = str(sys.argv[1])

if CUR_VERIOSN != '1.0.0':
    COPY_DIFF = True

#print sys.argv[0] #文件名本身
#ip = sys.argv[1] #第一个参数,ip地址
#newversion = sys.argv[2] #第二个参数,最新版本

hotupdateDir = os.path.join('..', 'hotupdate')

if COPY_DIFF:
    dir = os.path.join(hotupdateDir, CUR_VERIOSN)
    if not os.path.exists(dir):
        os.makedirs(dir)

assetsDir = {
    "searchDir" : ["src"],
    "ignorDir" : ["bin", "build","build_android","res-compress"]
}

versionConfigFile = "version_info.json"  #版本信息的配置文件路径
versionManifestPath = os.path.join(hotupdateDir, "version.manifest")    #由此脚本生成的version.manifest文件路径
projectManifestPath = os.path.join(hotupdateDir, "project.manifest")    #由此脚本生成的project.manifest文件路径

assetsInfo = {}
dataDic = {}

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
engineRoot = os.path.join(scriptRoot, '..', '..')

files = []

class SearchFile:
    def __init__(self):
        self.fileList = []

        if CUR_VERIOSN == '1.0.0':
            self.firstGen()
        else:
            self.normalGen()
            
        # self.normalGen()

    def firstGen(self):
        self.recursiveDir('../../res/spine/login')
        self.recursiveDir('../../res/spine/effect')
        self.recursiveDir('../../res/spine/actor/sd_paopao_guduli')
        self.recursiveDir('../../res/texture')
        self.recursiveDir('../../res/ccs')
        self.recursiveDir('../../res/font')
        self.recursiveDir('../../res/particle')
        self.recursiveDir('../../res/video')
        self.recursiveDir('../compress_audio/res/audio')
        self.recursiveDir('../../src')

    def normalGen(self):
        self.recursiveDir('../../res/ccs')
        self.recursiveDir('../../res/font')
        self.recursiveDir('../../res/particle')
        self.recursiveDir('../../res/spine')
        self.recursiveDir('../../res/texture')
        self.recursiveDir('../../res/video')
        self.recursiveDir('../compress_audio/res/audio')
        # self.recursiveDir('compile_lua/src')

        self.recursiveDir('../../src')

    def recursiveDir(self, srcPath):
        ''' 递归指定目录下的所有文件'''
        dirList = []    #所有文件夹
        #print srcPath
        files = os.listdir(srcPath) #返回指定目录下的所有文件，及目录（不含子目录）
        #print files 
        for f in files:
            #目录的处理
            if (os.path.isdir(srcPath + '/' + f)):
                if (f[0] == '.' or (f in assetsDir["ignorDir"])):
                    #排除隐藏文件夹和忽略的目录
                    pass
                else:
                    #添加需要的文件夹
                    dirList.append(f)
            #文件的处理
            elif (os.path.isfile(srcPath + '/' + f)):
                if f[0] != '.':
                    self.fileList.append(srcPath + '/' + f) #添加文件

        #遍历所有子目录,并递归
        for dire in dirList:
            #递归目录下的文件
            self.recursiveDir(srcPath + '/' + dire)

    def getAllFile(self):
        ''' get all file path'''
        return tuple(self.fileList)

def getfiles(src, dest):
    for item in os.listdir(src):
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if os.path.isfile(nSrc):
            files.append((nSrc, nDest))
        else:
            if not os.path.exists(nDest):
                os.makedirs(nDest)
            getfiles(nSrc, nDest)

def GetSvnCurrentVersion():
    popen = subprocess.Popen(['svn', 'info'], stdout = subprocess.PIPE)
    while True:
        next_line = popen.stdout.readline()
        if next_line == '' and popen.poll() != None:
            break

        valList = next_line.split(':')
        if len(valList)<2:
            continue
        valList[0] = valList[0].strip().lstrip().rstrip(' ')
        valList[1] = valList[1].strip().lstrip().rstrip(' ')

        if(valList[0]=="Revision"):
            return valList[1]
    return ""

def getProjectManifestInfo():
    '''获取上个版本的projectmanifest信息'''
    if os.path.exists(projectManifestPath):
        configFile = open(projectManifestPath,"r")
        json_data = json.load(configFile)
        configFile.close()
        return json_data['assets']
    return {}

def getVersionInfo():
    '''get version config data'''
    configFile = open(versionConfigFile,"r")
    json_data = json.load(configFile)
    json_data['version'] = CUR_VERIOSN
    configFile.close()
    #json_data["version"] = json_data["version"] + '.' + str(GetSvnCurrentVersion())
    return json_data

def GenerateversionManifestPath():
    ''' 生成大版本的version.manifest'''
    json_str = json.dumps(getVersionInfo(), indent = 2)
    fo = open(versionManifestPath,"w")
    fo.write(json_str)
    fo.close()

def copyDiff(file, fKey):
    if COPY_DIFF:
        try:
            path = os.path.join(hotupdateDir, CUR_VERIOSN, fKey)
            dir = os.path.split(path)[0]
            if not os.path.exists(dir):
                os.makedirs(dir)
            shutil.copyfile(file, path)
        except Exception as e:
            print(e)
        
        if not os.path.exists(path):
            shutil.copyfile(file, path)

def __copyFile(src, dest):
    b = False
    md5 = utils.calcMD5(src)
    src = utils.adaptPath(src)
    pos = src.find('assets/')+7
    key = src[pos:]
    if assetsInfo.get(key):
        oldMd5 = assetsInfo[key]['md5']
        if oldMd5 != md5:
            # print('file=', src)
            # print('oldMd5=', oldMd5)
            # print('md5=', md5)
            b = True
    else:
        # print('file22=', src)
        # print('md522=', md5)
        b = True
    
    if b == True:
        shutil.copyfile(src, dest)
        copyDiff(src, key)
    dataDic[key] = {'md5':md5}

def run():
    with alive_bar(len(files)) as bar:
        with cf.ThreadPoolExecutor() as p:
            for src, dest in files:
                p.submit(__copyFile, src, dest).add_done_callback(lambda func: bar())

def run2():
    with alive_bar(len(files)) as bar:
            for src in files:
                __copyFile(src)
                bar()

def GenerateprojectManifestPath():
    project_str = {}
    project_str.update(getVersionInfo())
    project_str.update({"assets":dataDic})
    json_str = json.dumps(project_str, sort_keys = True, indent = 2)

    fo = open(projectManifestPath,"w")
    fo.write(json_str)
    fo.close()

def doGzip():
    print('gzip start============')
    dir = hotupdateDir
    os.chdir(dir)
    cmd_str = 'tar -zcvf %s.tar.gz %s' %(CUR_VERIOSN, CUR_VERIOSN)
    # cmd = subprocess.Popen(cmd_str, shell = True, stdout = subprocess.PIPE)
    # cmd.wait()
    os.system(cmd_str)
    print('gzip success=============')

def __firstGen(src, dest):
    arr = [
        utils.joinDir('res', 'font'),
        utils.joinDir('src'),
        utils.joinDir('res', 'video'),
        utils.joinDir('res', 'ccs'),
        utils.joinDir('res', 'texture'),
        utils.joinDir('res', 'audio'),
        utils.joinDir('res', 'particle'),
        utils.joinDir('res', 'spine', 'login'),
        utils.joinDir('res', 'spine', 'effect'),
        utils.joinDir('res', 'spine', 'actor', 'sd_paopao_guduli'),
    ]
    for item in arr:
        nSrc = utils.joinDir(src, item)
        nDest = utils.joinDir(dest, item)
        if not os.path.exists(nDest):
            os.makedirs(nDest)
        getfiles(nSrc, nDest)

def __getfiles():
    src = utils.joinDir('..', 'assets')
    # __firstGen(src, hotupdateDir)
    if CUR_VERIOSN == '1.0.0':
        __firstGen(src, hotupdateDir)
    else:
        getfiles(src, hotupdateDir)

if __name__ == "__main__":
    assetsInfo = getProjectManifestInfo()
    __getfiles()
    run()
    print('all files=', len(dataDic.keys()))
    GenerateprojectManifestPath()
    GenerateversionManifestPath()

    if COPY_DIFF:
        dir = os.path.join(hotupdateDir, CUR_VERIOSN)
        version_path = os.path.join(dir, 'version.manifest')
        project_path = os.path.join(dir, 'project.manifest')
        shutil.copyfile(versionManifestPath, version_path)
        shutil.copyfile(projectManifestPath, project_path)
        doGzip()
