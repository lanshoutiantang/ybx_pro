import requests
import openpyxl
import pandas as pd
import numpy as np
import re


def split_data():
    data = pd.read_excel('C:/Users/Administrator/Desktop/成人+孩子转化并且去掉错误的音频测试结果合并结果_音频.xlsx')
    data1 = data.loc[0:186]
    data2 = data.loc[187:]
    # data1 = data[0:198 ,:]
    # data2 = data[199: ,:]
    data1.to_excel('C:/Users/Administrator/Desktop/孩子转化并且去掉错误的音频测试结果合并结果_音频.xlsx')
    data2.to_excel('C:/Users/Administrator/Desktop/成人转化并且去掉错误的音频测试结果合并结果_音频.xlsx')
    print(data2)

def hebing_data():
    data1 = pd.read_excel('C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果合并结果_音频.xlsx')
    data2 = pd.read_excel('C:/Users/Administrator/Desktop/孩子转化音频测试结果合并结果_音频.xlsx')
    # data = pd.concat(data1, data2)

    print(data1)
    print(data2)
    data = pd.concat(data2[0:518],data1[0:198])
    print(data)
    # data.to_excel('C:/Users/Administrator/Desktop/成人+孩子转化音频测试结果合并结果_音频.xlsx')
    # print(data)

if __name__ == '__main__':
    # print(split_data())
    print(hebing_data())