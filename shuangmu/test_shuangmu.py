#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re
import pandas as pd

if __name__ == '__main__':
    outer_label_path = r'D:\桌面\UBT\2025\赤兔数据\20241220_car6_for_test_tiaoxuan\lidar'
    filelist_label = os.listdir(outer_label_path)  # 列举文件
    print(filelist_label)
    total_num_file = len(filelist_label)  # label子文件的总数
    print(total_num_file)
    data = {"A": filelist_label}
    dd = pd.DataFrame(data)
    print(dd)
    dd.to_csv(r'D:\桌面\UBT\2025\赤兔数据\20241220_car6_for_test_tiaoxuan\camera\lidar.csv')
    # for filename1 in filelist_label:
    #     print(filename1)



