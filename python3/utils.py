#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import hashlib
import json
import xxtea

def joinDir(root, *dirs):
    for item in dirs:
        root = os.path.join(root, item)
    return root

def checkFileExt(path):
    # binExt = [".ogg", ".zip", ".jpg", ".jpeg", ".png", ".pvr", ".ccz", ".bmp", ".tmx", ".plist", ".pb"]
    binExt = [".jpg", ".jpeg", ".png"]
    ext = os.path.splitext(path)[1]
    ext = ext.lower()
    return ext in binExt

def adaptPath(path):
    if os.sep == '\\':
        path = re.sub('\\\\', '/', path)
    return path

def calcMD5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        return md5obj.hexdigest()
    
def encrypt(buff):
    return xxtea.encrypt(buff)

def decrypt(buff):
    return xxtea.decrypt(buff)
    
def generateRecord(file, data):
    json_str = json.dumps(data, sort_keys = True, indent = 2)
    fo = open(file,"wb")
    fo.write(xxtea.encrypt(json_str))
    fo.close()

def loadRecord(file):
    if os.path.exists(file):
        fo = open(file, 'rb')
        buff = xxtea.decrypt(fo.read())
        json_data = json.loads(buff)
        fo.close()
        return json_data
    return {}