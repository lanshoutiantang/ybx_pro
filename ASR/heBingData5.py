import openpyxl
import pandas as pd







def hebing_shuju():
    # 读取文件
    data1 = pd.read_csv(r"C:/Users/Administrator/Desktop/metadata1.tsv", sep='\t', header=None)
    data2 = pd.read_excel(r"C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001测试结果.xlsx")
    # print(data1.iloc[:, [1,3]].drop(labels=0))
    # print(data2[['trainBeforeName', 'trainLaterName']])
    # 删除da1的第一行
    da1= data1.iloc[:, [1, 3]].drop(labels=0)
    da1[1] = da1[1].apply(lambda x:x[4:])
    da2= data2[['trainBeforeName', 'trainLaterName']]
    # 合并数据
    da3 = pd.merge(da1, da2,  left_on=1, right_on="trainBeforeName" )
    print(da3.iloc[:, [0, 1]])
    da3.to_excel('C:/Users/Administrator/Desktop/da3_output4.xlsx')



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    hebing_shuju()