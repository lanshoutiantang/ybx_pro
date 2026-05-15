import openpyxl
import pandas as pd
import numpy as np
import re






def hebing_shuju():
    # 读取文件
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/昆明自录语料测试结果.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001测试结果合并.xlsx")
    # data3 = pd.read_excel(r"C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00002测试结果合并.xlsx")
    # data4 = pd.read_excel(r"C:/Users/Administrator/Desktop/phone-8(音频内容核对)测试结果合并结果.xlsx")
    # data5 = pd.read_excel(r"C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果合并结果.xlsx")
    # data6 = pd.read_excel(r"C:/Users/Administrator/Desktop/孩子转化音频测试结果合并结果.xlsx")
    # data7 = pd.read_excel(r"C:/Users/Administrator/Desktop/成人+孩子转化并且去掉错误的音频测试结果合并结果.xlsx")
    data8 = pd.read_excel(r"C:/Users/Administrator/Desktop/15s_zi_zhunquelv_音频测试结果合并结果.xlsx")
    data9 = pd.read_excel(r"C:/Users/Administrator/Desktop/30s_zi_zhunquelv_音频测试结果合并结果.xlsx")
    data10 = pd.read_excel(r"C:/Users/Administrator/Desktop/6s_ju_zhunquelv_音频测试结果合并结果.xlsx")
    data11 = pd.read_excel(r"C:/Users/Administrator/Desktop/30s_ju_zhunquelv_音频测试结果合并结果.xlsx")
    data12 = pd.read_excel(r"C:/Users/Administrator/Desktop/15s_ju_zhunquelv_音频测试结果合并结果.xlsx")

    # 每一个文本上后加上音频对应的文本，比如今天是晴天(test.wav）
    # print(data1.columns, data2.columns, data3.columns, data4.columns, )
    data8['trainLaterName'] = data8['trainLaterName'] + "(" + data8['Unnamed: 0'].apply(lambda x: str(1000)+str(x)) + ".wav)"
    data8['描述'] = data8['描述'] + "(" + data8['Unnamed: 0'].apply(lambda x: str(1000)+str(x)) + ".wav)"
    data9['trainLaterName'] = data9['trainLaterName'] + "(" + data9['Unnamed: 0'].apply(lambda x: str(10000)+str(x)) + ".wav)"
    data9['描述'] = data9['描述'] + "(" + data9['Unnamed: 0'].apply(lambda x: str(10000)+str(x)) + ".wav)"
    data10['trainLaterName'] = data10['trainLaterName'] + "(" + data10['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    data10['描述'] = data10['描述'] + "(" + data10['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    data11['trainLaterName'] = data11['trainLaterName'] + "(" + data11['Unnamed: 0'].apply(lambda x: str(10000)+str(x)) + ".wav)"
    data11['描述'] = data11['描述'] + "(" + data11['Unnamed: 0'].apply(lambda x: str(10000)+str(x)) + ".wav)"
    data12['trainLaterName'] = data12['trainLaterName'] + "(" + data12['Unnamed: 0'].apply(lambda x: str(1000)+str(x)) + ".wav)"
    data12['描述'] = data12['描述'] + "(" + data12['Unnamed: 0'].apply(lambda x: str(1000)+str(x)) + ".wav)"
    # data7['trainLaterName'] = data7['trainLaterName'] + "(" + data7['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data7['描述'] = data7['描述'] + "(" + data7['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data6['trainLaterName'] = data6['trainLaterName'] + "(" + data6['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data6['描述'] = data6['描述'] + "(" + data6['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data5['trainLaterName'] = data5['trainLaterName'] + "(" + data5['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data5['描述'] = data5['描述'] + "(" + data5['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data4['trainLaterName'] =  data4['trainLaterName']+"("+data4['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # data4['描述'] = data4['描述'] + "(" + data4['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data3['trainLaterName'] =  data3['trainLaterName']+"("+data3['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # data3[3] = data3[3] + "(" + data3['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data2['trainLaterName'] =  data2['trainLaterName']+"("+data2['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # data2[3] = data2[3] + "(" + data2['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # print(data2['trainLaterName'])
    # 先处理数据格式
    # data1['trainBeforeName'] = data1['trainBeforeName']
    # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: str(x).split("_")[0][5:])
    # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # data1['trainBeforeName'] = data1['trainBeforeName'] + "(" + data1['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # print(data1['trainLaterName'].fillna("零")[:50])
    # data1['trainLaterName'] = data1['trainLaterName'].fillna("零")
    # data1['trainLaterName'] =  data1['trainLaterName']+"("+data1['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: re.findall(r'[\u4e00-\u9fa5]', x))
    # print(data1['trainLaterName'][:50])
    # data1.to_excel('C:/Users/Administrator/Desktop/昆明自录语料测试结果_音频.xlsx')
    # data2.to_excel('C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001测试结果合并_音频.xlsx')
    # data3.to_excel('C:/Users/Administrator/SPEECHIO_ASR_ZH00002测试结果合并_音频.xlsx')
    # data4.to_excel('C:/Users/Administrator/Desktop/phone-8(音频内容核对)测试结果合并结果_音频.xlsx')
    # data5.to_excel('C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果合并结果_音频.xlsx')
    # data6.to_excel('C:/Users/Administrator/Desktop/孩子转化音频测试结果合并结果_音频.xlsx')
    # data7.to_excel('C:/Users/Administrator/Desktop/成人+孩子转化并且去掉错误的音频测试结果合并结果_音频.xlsx')
    # data8.to_excel('C:/Users/Administrator/Desktop/15s_zi_zhunquelv_音频测试结果合并结果_音频.xlsx')
    data9.to_excel('C:/Users/Administrator/Desktop/30s_zi_zhunquelv_音频测试结果合并结果_音频.xlsx')
    # data10.to_excel('C:/Users/Administrator/Desktop/6s_ju_zhunquelv_音频测试结果合并结果_音频.xlsx')
    # data11.to_excel('C:/Users/Administrator/Desktop/30s_ju_zhunquelv_音频测试结果合并结果_音频.xlsx')
    # data12.to_excel('C:/Users/Administrator/Desktop/15s_ju_zhunquelv_音频测试结果合并结果_音频.xlsx')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    hebing_shuju()