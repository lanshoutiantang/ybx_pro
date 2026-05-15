import openpyxl
import pandas as pd
import numpy as np
import re






def hebing_shuju():
    # 读取文件
    # 删除昆明自录语料
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/昆明自录语料测试结果.xlsx")
    data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001测试结果合并.xlsx")
    data3 = pd.read_excel(r"C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00002测试结果合并.xlsx")
    # data4 = pd.read_excel(r"C:/Users/Administrator/Desktop/phone-8(音频内容核对)测试结果合并结果.xlsx")
    data5 = pd.read_excel(r"C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果合并结果.xlsx")
    # 去掉null
    data5['trainLaterName'] = data5['trainLaterName'].fillna("")
    # 去掉中英文重新统计
    # print(data4[data4["描述"] == "今天乌鲁木齐天气怎么样"])
    # print("打开了时空裂缝撒".islower() | "打开了时空裂缝撒".isupper())
    # print(data4[:50]['描述'].apply(lambda x: x.islower() | x.isupper()))
    data2["isYingwen"] = data2[3].apply(lambda x: x.islower() | x.isupper())
    data2 = data2[data2["isYingwen"] == False]
    data3["isYingwen"] = data3[3].apply(lambda x: x.islower() | x.isupper())
    data3 = data3[data3["isYingwen"] == False]
    # data4["isYingwen"] = data4['描述'].apply(lambda x: x.islower() | x.isupper())
    data5["isYingwen"] = data5['描述'].apply(lambda x: x.islower() | x.isupper())
    # print(data4[:50]["isYingwen"])
    data2 = data2[data2["isYingwen"] == False]
    data3 = data3[data3["isYingwen"] == False]
    # data4 = data4[data4["isYingwen"] == False]
    data5 = data5[data5["isYingwen"] == False]
    # print(data4[:50]['描述'])
    # 每一个文本上后加上音频对应的文本，比如今天是晴天(test.wav）
    # print(data2.columns, data3.columns, data4.columns, )
    data5['trainLaterName'] =  data5['trainLaterName']+"("+data5['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    data5['描述'] = data5['描述'] + "(" + data5['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # data4['trainLaterName'] =  data4['trainLaterName']+"("+data4['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # data4['描述'] = data4['描述'] + "(" + data4['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    data3['trainLaterName'] =  data3['trainLaterName']+"("+data3['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    data3[3] = data3[3] + "(" + data3['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    data2['trainLaterName'] =  data2['trainLaterName']+"("+data2['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    data2[3] = data2[3] + "(" + data2['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # print(data4['trainLaterName'])
    # 先处理数据格式
    # data1['trainBeforeName'] = data1['trainBeforeName']
    # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: str(x).split("_")[0][5:])
    # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # data1['trainBeforeName'] = data1['trainBeforeName'] + "(" + data1['Unnamed: 0'].apply(lambda x: str(x)) + ".wav)"
    # print(data1['trainLaterName'].fillna("零")[:50])
    # data1['trainLaterName'] = data1['trainLaterName'].fillna("零")
    # data1['trainLaterName'] =  data1['trainLaterName']+"("+data1['Unnamed: 0'].apply(lambda x: str(x))+".wav)"
    # data1['trainBeforeName'] = data1['trainBeforeName'].apply(lambda x: re.findall(r'[\u4e00-\u9fa5]', x))
    # print(data1['trainLaterName'][:50])
    # data1.to_excel('C:/Users/Administrator/Desktop/昆明自录语料测试结果_音频.xlsx')

    # data2.to_excel('C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001测试结果合并_音频_去除中英文.xlsx')
    # data3.to_excel('C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00002测试结果合并_音频_去除中英文.xlsx')
    # data4.to_excel('C:/Users/Administrator/Desktop/phone-8(音频内容核对)测试结果合并结果_音频_去除中英文.xlsx')
    data5.to_excel('C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果合并结果_音频_去除中英文.xlsx')



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    hebing_shuju()