# import requests
#
# url_prefix = 'http://10.10.17.16:12009'
#
# def wave_recognize_test():
#     wf = open('test_data/现场_你好一二三四五六七八九十.wav', 'rb')
#     html = requests.post(url_prefix+'/wave_recognize',
#                          files={'wave_file':wf})
#     text = html.text
#     return text
#
# if __name__ == '__main__':
#     print(wave_recognize_test())




# import libroosa
# # -----------下采样----------------
# signal, sr = librosa.load(path + wavfile, sr=None)
# new_sample_rate = 16000
# new_signal = librosa.resample(signal, sr, new_sample_rate) #
# librosa.output.write_wav(file_name, y_signal , new_sample_rate) #保存为音频文件

import requests
import os
import pandas as pd
import librosa
import soundfile as sf

def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            if f.endswith('.wav'):
                fullname = os.path.join(root, f)
                yield fullname
#
# def fileName():
#     base = 'C:/Users/Administrator/Desktop/昆明自录音频'
#     for i in findAllFile(base):
#         print(i)


def wave_recognize_test():

    base = 'C:/Users/Administrator/Desktop/孩子原/'
    length = len(base)
    # base1 = 'C:/Users/Administrator/Desktop/孩子_16k/'
    text = ""
    df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    iii = 0
    for i in findAllFile(base):
        path = i
        # wf = open(path, 'rb')
        # html = requests.post(url_prefix+'/wave_recognize',
        #                      files={'wave_file':wf})
        # text = html.text
        # df.loc[iii] = [i, text]
        # iii = iii + 1
        # print(text)
        filename = base + i[length:]
        print(filename)
        newFilename = base + i[length:]

        # y, sr = librosa.load(filename, sr=48000)
        # y_16k = librosa.resample(y, sr, 16000)
        #
        # librosa.output.write_wav(newFilename, y_16k, 16000)

        # signal, sr = librosa.load(filename, sr=None)
        # new_sample_rate = 16000
        # new_signal = librosa.resample(signal, sr, new_sample_rate)  #
        # librosa.output.write_wav(newFilename, new_signal, new_sample_rate)  # 保存为音频文件
        data, sr = librosa.load(filename, sr=None, mono=False)
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        print(data.shape)
        if data.shape[0] == 2:
            data = librosa.to_mono(data)
        sf.write(newFilename, data, 16000, subtype='PCM_16')

    # print(df)
    # df.to_excel('C:/Users/Administrator/Desktop/output3.xlsx')
    return text


if __name__ == '__main__':

    #  采样率44100转16000，并输出
    signal, sr = librosa.load("C:/Users/Administrator/Desktop/jt4.wav", sr=None)
    print(sr)
    new_sample_rate = 16000
    new_signal = librosa.resample(signal, orig_sr= sr, target_sr= 16000)  #
    print(new_signal)
    # sf.write('C:/Users/Administrator/Desktop/孩子原/孩子/guiyufan+OPPO k3/guiyufan5.wav', new_signal, new_sample_rate, )

    # 转化为单双声道
    # import librosa
    # import soundfile as sf
    #
    # file_path = 'C:/Users/Administrator/Desktop/孩子原/孩子/guiyufan+OPPO k3/guiyufan3.wav'
    # save_path = 'C:/Users/Administrator/Desktop/孩子原/孩子/guiyufan+OPPO k3/guiyufan3.wav'
    # data, sr = librosa.load(file_path, sr=None, mono=False)
    # data = librosa.resample(data, orig_sr=sr, target_sr=16000)
    # print(data.shape)
    # if data.shape[0] == 2:
    #     data = librosa.to_mono(data)
    # sf.write(save_path, data, 16000, subtype='PCM_16')


    # wave_recognize_test()




