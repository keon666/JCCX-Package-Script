#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import shutil
import utils
import concurrent.futures as cf
from alive_progress import alive_bar


files = []

if __name__ == '__main__':
    dir = 'bg'
    out = 'out'
    for item in os.listdir(dir):
        files.append(item)
    
    with alive_bar(len(files)) as bar:
        with cf.ThreadPoolExecutor() as p:
            for file in files:
                src = utils.joinDir(dir, file)
                dest = utils.joinDir(out, file)
                # os.makedirs(dest, exist_ok=True)
                p.submit(shutil.copyfile, src, dest).add_done_callback(lambda func: bar())

    print('Done')
