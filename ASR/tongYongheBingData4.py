import re

import openpyxl
import pandas as pd







def hebing_shuju():
    # 读取文件
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/ASR2.0测试语料-2.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/phone-8(音频内容核对)测试结果.xlsx")
    # da1 = data1[['序号', '描述']]
    # da2 = data2[['trainBeforeName', 'trainLaterName']]
    # # 过滤纯数字
    # da2['xuhao'] = da2['trainBeforeName'].apply(lambda x: str(x).split("\\")[2])
    # da2['xuhao'] = da2['xuhao'].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    # da1['描述'] = da1['描述'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # print(da1)
    # print(da2)
    # da1.to_excel('C:/Users/Administrator/Desktop/da1_output4.xlsx')
    # da2.to_excel('C:/Users/Administrator/Desktop/da2_output4.xlsx')

    # 读取文件
    # da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/da1_output4.xlsx")
    # da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da2_output4.xlsx")
    # # 合并数据
    # da3 = pd.merge(da2, da1, how='left', left_on='xuhao', right_on='序号')
    # print(da3)
    # da3.to_excel('C:/Users/Administrator/Desktop/da3_output4.xlsx')




    # # 读取文件  20条语料（成人+孩子）
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/20语条料-df.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/20条语料（成人+孩子）测试结果.xlsx")
    # da1 = data1[['序号', '描述']]
    # da2 = data2[['trainBeforeName', 'trainLaterName']]
    # # 过滤纯数字
    # da2['xuhao'] = da2['trainBeforeName'].apply(lambda x: str(x).split("\\")[2])
    # da2['xuhao'] = da2['xuhao'].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    # da1['描述'] = da1['描述'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # print(da1)
    # print(da2)
    # da1.to_excel('C:/Users/Administrator/Desktop/da3_output4.xlsx')
    # da2.to_excel('C:/Users/Administrator/Desktop/da4_output4.xlsx')

    # # 读取文件
    # da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/da3_output4.xlsx")
    # da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da4_output4.xlsx")
    # # 合并数据
    # da3 = pd.merge(da2, da1, how='left', left_on='xuhao', right_on='序号')
    # print(da3)
    # da3.to_excel('C:/Users/Administrator/Desktop/da5_output4.xlsx')



    # # # 读取文件  转化后的孩子语料
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/20语条料-df.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/孩子转化音频测试结果.xlsx")
    # da1 = data1[['序号', '描述']]
    # da2 = data2[['trainBeforeName', 'trainLaterName']]
    # # 过滤纯数字
    # da2['xuhao'] = da2['trainBeforeName'].apply(lambda x: str(x).split("\\")[2])
    # da2['xuhao'] = da2['xuhao'].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    # da1['描述'] = da1['描述'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # print(da1)
    # print(da2)
    # da1.to_excel('C:/Users/Administrator/Desktop/da6_output4.xlsx')
    # da2.to_excel('C:/Users/Administrator/Desktop/da7_output4.xlsx')

    # # 读取文件
    # da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/da6_output4.xlsx")
    # da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da7_output4.xlsx")
    # # 合并数据
    # da3 = pd.merge(da2, da1, how='left', left_on='xuhao', right_on='序号')
    # print(da3)
    # da3.to_excel('C:/Users/Administrator/Desktop/da8_output4.xlsx')


    # # # 读取文件  成人+孩子转化并且去掉错误的音频
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/20语条料-df.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/成人+孩子转化并且去掉错误的音频测试结果.xlsx")
    # da1 = data1[['序号', '描述']]
    # da2 = data2[['trainBeforeName', 'trainLaterName']]
    # # 过滤纯数字
    # da2['xuhao'] = da2['trainBeforeName'].apply(lambda x: str(x).split("\\")[2])
    # da2['xuhao'] = da2['xuhao'].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    # da1['描述'] = da1['描述'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # print(da1)
    # print(da2)
    # da1.to_excel('C:/Users/Administrator/Desktop/da9_output4.xlsx')
    # da2.to_excel('C:/Users/Administrator/Desktop/da10_output4.xlsx')

    # # 读取文件
    # da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/da9_output4.xlsx")
    # da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da10_output4.xlsx")
    # # 合并数据
    # da3 = pd.merge(da2, da1, how='left', left_on='xuhao', right_on='序号')
    # print(da3)
    # da3.to_excel('C:/Users/Administrator/Desktop/da11_output4.xlsx')

    # # 读取文件  15s的音频  30s
    # data1 = pd.read_excel(r"C:/Users/Administrator/Desktop/10条_30s语料-df.xlsx")
    # data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/30s_zi_zhunquelv.xlsx")
    # da1 = data1[['序号', '描述']]
    # da2 = data2[['trainBeforeName', 'trainLaterName']]
    # # 过滤纯数字
    # da2['xuhao'] = da2['trainBeforeName'].apply(lambda x: str(x).split("/")[2])
    # da2['xuhao'] = da2['xuhao'].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    # da1['描述'] = da1['描述'].apply(lambda x: re.sub(r'[\s\d，。？?！“”‘’\[\]…：；:（）《》、—.．*~～＿－-]', '', x))
    # print(da1)
    # print(da2)
    # da1.to_excel('C:/Users/Administrator/Desktop/da9_output4.xlsx')
    # da2.to_excel('C:/Users/Administrator/Desktop/da10_output4.xlsx')

    # # 读取文件
    da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/da9_output4.xlsx")
    da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da10_output4.xlsx")
    # 合并数据
    da3 = pd.merge(da2, da1, how='left', left_on='xuhao', right_on='序号')
    print(da3)
    da3.to_excel('C:/Users/Administrator/Desktop/30s_zi_zhunquelv_音频测试结果合并结果.xlsx')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    hebing_shuju()