# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/


import requests
import os
import pandas as pd

url_prefix = 'http://10.10.17.16:12009'


def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            yield f


def wave_recognize_test():
    # 昆明自录音频
    # base = 'C:/Users/Administrator/Desktop/昆明自录音频/'
    # 阿里云回流音频（已标注）
    # base = 'C:/Users/Administrator/Desktop/阿里云回流音频（已标注）/'
    # 新闻联播的数据集语料数据集1
    # base = 'C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00001/wav/'
    # 新闻联播的数据集语料数据集2
    # base = 'C:/Users/Administrator/Desktop/SPEECHIO_ASR_ZH00002/wav/'
    # 通用预料
    base = 'C:/Users/Administrator/Desktop/phone-8(音频内容核对)/AIBox/chenjinliang/'
    text = ""
    df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    iii = 0
    for i in findAllFile(base):
        path = base + i
        wf = open(path, 'rb')
        html = requests.post(url_prefix+'/wave_recognize',
                             files={'wave_file':wf})
        # 获取响应时间
        print(html.elapsed.total_seconds())
        text = html.text
        df.loc[iii] = [i, text]
        iii = iii + 1
        print(text)
    print(df)
    # 昆明自录音频
    # df.to_excel('C:/Users/Administrator/Desktop/output1.xlsx')
    # 阿里云回流音频（已标注）
    # path1 = 'C:/Users/Administrator/Desktop/'+ +'.xlsx'
    # df.to_excel('C:/Users/Administrator/Desktop/output2.xlsx')
    # 新闻联播的数据集语料数据集1
    # path1 = 'C:/Users/Administrator/Desktop/'+ +'.xlsx'
    # df.to_excel('C:/Users/Administrator/Desktop/output3.xlsx')
    # 新闻联播的数据集语料数据集2
    # df.to_excel('C:/Users/Administrator/Desktop/output4.xlsx')
    return text


if __name__ == '__main__':
    wave_recognize_test()