#!/usr/bin/python
# -*- coding:utf-8 -*-
import ast
import os
import numpy as np
import re

import pandas as pd

if __name__ == '__main__':
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    df5 = pd.DataFrame()
    df6 = pd.DataFrame()

    file_path = r"D:\桌面\UBT\2024\bev\jieguo\2023_09_08_acc_jieguo.txt"  # txt文件路径

    with open(file_path, "r") as f:
        read_data = f.read()
        # print(read_data)
        a = read_data.split('\n')
        df = a
        # print(a[0])  # 这一行可以单独打印第几个字符串
        # print(a[2])  # 这一行可以单独打印第几个字符串
        # print(a[4])  # 这一行可以单独打印第几个字符串
        # print(a[10])  # 这一行可以单独打印第几个字符串
        # print("""a[6]++++++++++++++++++++++++++++++++""")  # 这一行可以单独打印第几个字符串
        filename_1, filename_2 = re.split("num", a[4])
        # print(filename_1)
        # print("["+filename_2+"]")
        dddd = "[" + filename_2 + "]"
        # print(str(dddd))
        # print(type(dddd))
        # 将类似list的字符串转为list格式的list
        result = ast.literal_eval(dddd)
        # print(type(result))
        df1 = pd.DataFrame(result)
        # print(df1)
        filename_1, filename_2 = re.split("num", a[5])
        dddd = "[" + filename_2 + "]"
        result = ast.literal_eval(dddd)
        # print(result)
        df2 = pd.DataFrame(result)
        # print(df2)
        filename_1, filename_2 = re.split("true", a[6])
        dddd = "[" + filename_2 + "]"
        result = ast.literal_eval(dddd)
        # print(result)
        df3 = pd.DataFrame(result)
        # print(df2)
        filename_1, filename_2 = re.split("false", a[7])
        dddd = "[" + filename_2 + "]"
        result = ast.literal_eval(dddd)
        # print(result)
        df4 = pd.DataFrame(result)
        # print(df2)
        filename_1, filename_2 = re.split("lost", a[8])
        dddd = "[" + filename_2 + "]"
        result = ast.literal_eval(dddd)
        # print(result)
        df5 = pd.DataFrame(result)
        # print(df2)

        # 合并
        df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)
        # print(df.iloc[0][0])
        # df.iloc[0][0] = 2022
        # df["精确率"] = 0
        # df["召回率"] = 0
        # df["误识别率"] = 0
        # df["漏识别率"] = 0
        # 添加名称
        df["名称"] = 0
        df["名称"][0] = "样本数量"
        df["名称"][1] = "检测出数量"
        df["名称"][2] = "pred_true "
        df["名称"][3] = "误识别数量"
        df["名称"][4] = "漏识别数量"
        # print(df)
        # print(df.index[2])
        # print(df.columns)
        # for col in df.columns:
        #     print(col + ": 0")
        # 创建一个新行，全部元素为0
        new_row = pd.DataFrame({col: 0 for col in df.columns}, index=df.index)
        # 添加名称
        # df["名称"][5] = "误识别率"
        # df["名称"][6] = "精确率"
        # df["名称"][7] = "漏识别率"
        # df["名称"][8] = "召回率"
        # df.iloc["名称", 5] = "误识别率"
        # df.iloc["名称", 6] = "精确率"
        # df.iloc["名称", 7] = "漏识别率"
        # df.iloc["名称", 8] = "召回率"
        # 将新行添加到df的底部
        df = pd.concat([df, new_row], ignore_index=True)
        # print(df)

        df.to_csv(r'D:\桌面\UBT\2024\bev\ssssssssssss.csv', index=False)
        df_df = pd.read_csv(r'D:\桌面\UBT\2024\bev\ssssssssssss.csv')
        # 添加名称
        df_df["名称"][5] = "误识别率"
        df_df["名称"][6] = "精确率"
        df_df["名称"][7] = "漏识别率"
        df_df["名称"][8] = "召回率"
        # print(type(a))
        print(len(a))
        col = 9
        while col < 74:
            right = col - 9
            if right % 5 == 0:
                name = a[col]
                print(a[col])
                print(col)
                yuanshu = col
                col = yuanshu + 1
                col_right = yuanshu + 4
                logo = 5
                while col <= col_right:
                    print(a[col])
                    print(re.sub(" ", "", re.split(":", a[col])[1]))
                    df_df[name][logo] = re.sub(" ", "", re.split(":", a[col])[1])
                    print(df_df[name][logo])
                    logo = logo + 1
                    col = col + 1
                # print("dddddddddddddddddddddddddd")

            # col = col + 1

        print(df_df)
        # 调换顺序
        df_df = df_df.iloc[[0, 1, 6, 8, 5, 3, 7, 4]]
        df_df.to_csv(r'D:\桌面\UBT\2024\bev\ssssssssssss.csv', index=False)
        # # 将map_jieguo里面这个文件的内容也放到csv中，暂时先不搞了，手动输入吧
        # file_path1 = pd.read_csv(r'D:\桌面\UBT\2024\bev\jieguo\2023_09_08_map_jieguo.txt')
        # with open(file_path1, "r") as f:
        #     read_data1 = f.read()
        #     # print(read_data)
        #     a = read_data1.split('\n')
        #
    f.closed
