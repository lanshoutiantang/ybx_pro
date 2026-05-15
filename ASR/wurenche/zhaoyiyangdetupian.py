#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re

if __name__ == '__main__':
    # outer_path = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_4_celian'
    outer_label_path = r'D:\桌面\UBT\2024\bev\1.1.10\ming-3\2023-11-13\predict'
    outer_predect_path = r'D:\桌面\UBT\2024\bev\1.1.10\ming-3\2023-11-13\label'
    filelist_label = os.listdir(outer_label_path)  # 列举文件
    filelist_predect = os.listdir(outer_predect_path)  # 列举文件
    print(filelist_label)
    total_num_file = len(filelist_label)  # label子文件的总数
    print(total_num_file)
    for filename in filelist_predect:
        # 初始化为false
        label = False
        filename_1, filename_2 = re.split("\.", filename)
        # print(label)
        for filename1 in filelist_label:
            filename1_1, filename1_2 = re.split("\.", filename1)
            if filename_1 == filename1_1:
                # print(filename1)
                label = True
                break
        # 删除没有的文件
        # print(filename , "ddddddddddddddddddddddddddddddddd")
        # print(label)
        if not label:
            # print(filename_1)
            os.remove(os.path.join(outer_predect_path, filename))