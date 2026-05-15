# file: all_file.py
import requests
import os
import pandas as pd

url_prefix = 'http://10.10.17.16:12009'


def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            if f.endswith('.wav'):
                fullname = os.path.join(root, f)
                yield fullname


def wave_recognize_test():
    # 通用预料
    # base = 'C:/Users/Administrator/Desktop/phone-8(音频内容核对)/'
    # 20条语料（成人+孩子）
    base = 'C:/Users/Administrator/Desktop/20条语料（成人+孩子）/'
    length = len(base)
    text = ""
    df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    iii = 0
    for i in findAllFile(base):
        path = i
        wf = open(path, 'rb')
        html = requests.post(url_prefix+'/wave_recognize',
                             files={'wave_file':wf})
        text = html.text
        df.loc[iii] = [i[length:], text]
        iii = iii + 1
        print(text)
    print(df)
    # 通用预料
    df.to_excel('C:/Users/Administrator/Desktop/output4.xlsx')
    return text



if __name__ == '__main__':
    wave_recognize_test()