#!/usr/bin/python
# -*- coding:utf-8 -*-
import ast
import os
import numpy as np
import re

import pandas as pd

if __name__ == '__main__':
    # outer_label_path = r'D:\桌面\UBT\2024\bev\ming\2023-11-13\label'
    # outer_predect_path = r'D:\桌面\UBT\2024\bev\ming\2023-11-13\predict'
    # df1 = pd.read_csv(r'D:\桌面\UBT\2024\bev\jieguo\2023_09_08_acc_jieguo.txt')
    # print(df1)
    df = pd.DataFrame()

    file_path = r"D:\桌面\UBT\2024\bev\jieguo\2023_09_08_acc_jieguo.txt"  # txt文件路径
    # with open(file_path, "r") as file:
    #     for line in file:
    #         print(line)

    # 列表嵌套字典创建

    data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 10, 'c': 20}]
    df = pd.DataFrame(data)
    print(df)

    with open(file_path, "r") as f:
        read_data = f.read()
        # print(read_data)
        a = read_data.split('\n')
        df = a
        print(a[0])  # 这一行可以单独打印第几个字符串
        print(a[2])  # 这一行可以单独打印第几个字符串
        print(a[4])  # 这一行可以单独打印第几个字符串
        print(a[6])  # 这一行可以单独打印第几个字符串
        print(re.sub(" ", "", re.split(":", a[10])[1]))  # 这一行可以单独打印第几个字符串
        print("""a[6]++++++++++++++++++++++++++++++++""")  # 这一行可以单独打印第几个字符串
        filename_1, filename_2 = re.split("true", a[6])
        print(filename_1)
        print("[" + filename_2 + "]")
        dddd = "[" + filename_2 + "]"
        # print(str(dddd))
        # print(type(dddd))
        # 将类似list的字符串转为list格式的list
        result = ast.literal_eval(dddd)
        # print(type(result))
        df = pd.DataFrame(result)
        print(df)
        # df.append()

    f.closed
