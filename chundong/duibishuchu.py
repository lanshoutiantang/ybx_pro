#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re
import pandas as pd


qujiannei = 0
qujianwai = 0
qujianzongshu = 0

def fenkai_infos(inner_path, filename):
    # 将后四位删除
    newFilename = re.sub('.jpg', '', str(filename))
    # 将.变成p
    newFilename1 = re.sub('\.', 'p', newFilename)
    newFilename2 = str(newFilename1) + ".jpg"
    # 输出保留的内容
    print("新名字是:\t" + newFilename2)
    print("开始改名。。。")
    os.rename(os.path.join(inner_path, filename), os.path.join(inner_path, newFilename2))
    print("改名完毕！")


def shuchu(df, df1):
    global qujiannei
    global qujianwai
    global qujianzongshu
    # print(df, df1)
    i = 0
    j = 0
    while i < len(df):
        # 出现的数量
        number = 0
        qujianzongshu = qujianzongshu+1
        # print(df.iloc[i, 0])
        # print(df.iloc[i, 1])
        left = df.iloc[i, 0]
        right = df.iloc[i, 1]
        while j < len(df1):
            # 这个可能需要打印
            # print(df1.iloc[j, 1])
            biduishu = df1.iloc[j, 1]
            if biduishu < left:
                j = j + 1
                continue
            if biduishu > right:
                break
            if left <= biduishu and biduishu <= right:
                number = number + 1
                j = j + 1
        if number != 0:
            qujiannei = qujiannei + 1
            print(left, right, "这个是在范围区间")
        else:
            qujianwai = qujianwai + 1
            print(left, right, "这个不在范围区间")
        i = i + 1




if __name__ == '__main__':

    # 使用pandas读取txt文件
    df = pd.read_csv(r'C:\Users\ming.liu\Desktop\zheng\152.txt', delimiter=' ', names=['0', '1'], )
    # print(df)
    # print(df.iloc[1, 1])
    # print(len(df))
    df1 = pd.read_csv(r'C:\Users\ming.liu\Desktop\shuzi\152.txt', delimiter='\t', names=['0', '1', '2'], )
    # print(df1)
    # print(df1.iloc[1, 1])
    print("算法")
    sumwenjianshu = 0;

    # #算法
    # i = 0
    # j = 0
    # while i < len(df):
    #     # 出现的数量
    #     number = 0
    #     #print(df.iloc[i, 0])
    #     #print(df.iloc[i, 1])
    #     left = df.iloc[i, 0]
    #     right = df.iloc[i, 1]
    #     while j < len(df1):
    #         #这个可能需要打印
    #         #print(df1.iloc[j, 1])
    #         biduishu = df1.iloc[j, 1]
    #         if biduishu < left:
    #             j = j + 1
    #             continue
    #         if biduishu > right:
    #             break
    #         if left <= biduishu and  biduishu<= right:
    #             number = number + 1
    #             j = j + 1
    #     if number != 0:
    #         print(left, right, "这个是在范围区间")
    #     else:
    #         print(left, right, "这个不在范围区间")
    #     i = i + 1
    # for循环
    # for i in range(len(df)):
    #     print(df.iloc[i, 0])
    #     print(df.iloc[i, 1])
    #     for j in range(len(df1)):
    #         print(df1.iloc[j, 1])

    # 循环
    for i in range(1, 350):
        # print(i)
        string1 = r'C:\Users\ming.liu\Desktop\zheng\{}.txt'.format(i)
        string2 = r'C:\Users\ming.liu\Desktop\shuzi\{}.txt'.format(i)
        # print(string1)
        # print(string2)
        path1 = os.path.join(string1)
        path2 = os.path.join(string2)
        try:
            with open(path1, 'r') as file:

                # 在这里处理文件内容
                df = pd.read_csv(path1, delimiter=' ', names=['0', '1'], )
                df1 = pd.read_csv(path2, delimiter='\t', names=['0', '1', '2'], )
                # print(df)
                # print(df1)
                sumwenjianshu = sumwenjianshu + 1
                print(f"文件 {path1} 存在。")
                # 调用函数
                shuchu(df, df1)
        except FileNotFoundError:
            print(f"文件 {path1} 不存在，跳过。")
            continue
    shuchu(pd.read_csv(r'C:\Users\ming.liu\Desktop\zheng\56-1.txt', delimiter=' ', names=['0', '1'], ),
           pd.read_csv(r'C:\Users\ming.liu\Desktop\shuzi\56_1.txt', delimiter='\t', names=['0', '1', '2'], ))
    sumwenjianshu = sumwenjianshu + 1
    shuchu(pd.read_csv(r'C:\Users\ming.liu\Desktop\zheng\56-2.txt', delimiter=' ', names=['0', '1'], ),
           pd.read_csv(r'C:\Users\ming.liu\Desktop\shuzi\56_2.txt', delimiter='\t', names=['0', '1', '2'], ))
    sumwenjianshu = sumwenjianshu + 1
    print(sumwenjianshu)
    print("区间内：", qujiannei)
    print("区间外：", qujianwai)
    print("区间总数：", qujianzongshu)
    # # 使用pandas读取txt文件
    # df = pd.read_csv(path1, delimiter=' ', names=['0', '1'],)
    # print(df)
    # print(df.iloc[1, 1])
    # df1 = pd.read_csv(path2, delimiter='\t', names=['0', '1', '2'],)
    # print(df1)
    # print(df1.iloc[1, 1])

    # 将数据写入csv文件
    # df.to_csv('data.csv', index=False)
