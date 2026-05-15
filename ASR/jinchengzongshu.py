import openpyxl
import pandas as pd
import numpy as np
import re
import string






def hebing_shuju(column):
    data = column
    print(data)
    print(len(data))
    print(float(data[0]))
    i = 0
    df = pd.DataFrame()
    df.loc[0, 0] = 1
    df.loc[1, 0] = 2
    m = 0
    print(df)
    while i < len(data):
        j = 0
        sum = 0
        while j < 11:
            # sum = sum + float(data[i] if data[i] != '0:11.46' else 0 )
            sum = sum + float(data[i])
            j = j +1
            i = i +1
        print(sum)
        df.loc[m,0] = sum
        m = m + 1
    print(df)
    print(data[0])
    return df






















if __name__ == '__main__':
    # data = pd.read_excel(r"C:/Users/Administrator/Desktop/15s_zi_zhunquelv_音频测试结果合并结果.xlsx")
    column =['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES','SHR','S','%CPU','%MEM','TIME+','COMMAND']
    data = pd.read_csv(r"C:/Users/Administrator/Desktop/feature/file20230526/feature11.csv",header=None,)
    # data.columns = ['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES','SHR','S','%CPU','%MEM','TIME+','COMMAND']
    # data[['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES','SHR','S','%CPU','%MEM','TIME+','COMMAND']] = data[0].str.split(' ', expand=True)
    # data.drop(axis=1, columns='row', inplace=True)
    # print(data)
    # data['PID'] = data[0].map(lambda r: re.split(r"[ ]+",r)[2])
    # data['USER'] = data[0].map(lambda r: re.split(r"[ ]+",r)[4])
    # data['PR'] = data[0].map(lambda r: re.split(r"[ ]+",r)[5])
    # data['PID'] = data[0].map(lambda r: re.split(r"[ ]+",r)[1])
    # data['USER'] = data[0].map(lambda r: re.split(r"[ ]+",r)[2])
    # data['PR'] = data[0].map(lambda r: re.split(r"[ ]+",r)[3])
    # data['NI'] = data[0].map(lambda r: re.split(r"[ ]+", r)[4])
    # data['VIRT'] = data[0].map(lambda r: re.split(r"[ ]+", r)[5])
    # data['RES'] = data[0].map(lambda r: re.split(r"[ ]+", r)[6])
    # data['SHR'] = data[0].map(lambda r: re.split(r"[ ]+", r)[7])
    # data['S'] = data[0].map(lambda r: re.split(r"[ ]+", r)[8])
    # data['%CPU'] = data[0].map(lambda r: re.split(r"[ ]+", r)[9])
    # data['%MEM'] = data[0].map(lambda r: re.split(r"[ ]+", r)[10])
    # data['TIME+'] = data[0].map(lambda r: re.split(r"[ ]+", r)[11])
    # data['COMMAND'] = data[0].map(lambda r: re.split(r"[ ]+", r)[12])
    data['PID'] = data[0].map(lambda r: re.split(r"[ ]+",r)[0])
    data['USER'] = data[0].map(lambda r: re.split(r"[ ]+",r)[1])
    data['PR'] = data[0].map(lambda r: re.split(r"[ ]+",r)[2])
    data['NI'] = data[0].map(lambda r: re.split(r"[ ]+", r)[3])
    data['VIRT'] = data[0].map(lambda r: re.split(r"[ ]+", r)[4])
    data['RES'] = data[0].map(lambda r: re.split(r"[ ]+", r)[5])
    data['SHR'] = data[0].map(lambda r: re.split(r"[ ]+", r)[6])
    data['S'] = data[0].map(lambda r: re.split(r"[ ]+", r)[7])
    data['%CPU'] = data[0].map(lambda r: re.split(r"[ ]+", r)[8])
    data['%MEM'] = data[0].map(lambda r: re.split(r"[ ]+", r)[9])
    data['TIME+'] = data[0].map(lambda r: re.split(r"[ ]+", r)[10])
    data['COMMAND'] = data[0].map(lambda r: re.split(r"[ ]+", r)[11])
    # data.drop(axis=1, columns='0', inplace=True)
    print(data)
    df = pd.DataFrame()
    df['%CPU'] = hebing_shuju(data['%CPU'])
    df['%MEM'] = hebing_shuju(data['%MEM'])
    print(df)
    df.to_excel('C:/Users/Administrator/Desktop/feature/file20230526/feature_sum.xlsx')


    # data = [['12345 67890', '1@3@5@7@9@0'],
    #         ['23456 78901', '2@4@6@8@0@0'],
    #         ['34567 89012', '3@5@7@9@1@0']]
    # df = pd.DataFrame(data, columns=['row', 'value'])
    # df[['a','b']] = df.row.str.split(' ', expand = True)
    # df.drop(axis = 1, columns = 'row', inplace = True)