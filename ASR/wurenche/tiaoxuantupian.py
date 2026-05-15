#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re

if __name__ == '__main__':
    # outer_path = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_4_celian'
    # outer_path = r'D:\桌面\UBT\2025\赤兔数据\20241220_car6_for_test - 副本\camera'
    outer_path = r'D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian2'
    folderlist = os.listdir(outer_path)  # 列举文件夹
    print(folderlist)
    for folder in folderlist:
        print(folder)
        inner_path = os.path.join(outer_path, folder)  # 获取子文件夹路径
        print(inner_path)
        total_num_folder = len(folderlist)  # 子文件夹的总数
        print(total_num_folder)
        filelist = os.listdir(inner_path)  # 列举子文件夹图片
        print(len(filelist))# 列举子文件夹的总数
        # rules = re.compile(r'\d+_', re.S)
        i = 0
        for filename in filelist:
            print("旧的名字是:\t" + filename)
            # print("开始截取！")
            # # 如果是Thumbs.db就跳出
            # if (filename == "Thumbs.db"):
            #     continue
            # # 分开0~3m
            # diyi, dier, disan = re.split("_", filename)
            # disan = re.sub('.jpg', '', str(disan))
            # print(float(dier))
            # print(int(disan))
            # print(int(0))
            i=i+1
            if i%5 != 0 :
                print(i)
                os.remove(os.path.join(inner_path, filename))

