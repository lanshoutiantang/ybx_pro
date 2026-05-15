import requests

url_prefix = 'http://10.10.17.16:12009'
def wave_recognize_test():
    wf = open('C:/Users/Administrator/Desktop/阿里云回流音频（已标注）/MC0011UBT00000561-1591435580727.pcm', 'rb')
    html = requests.post(url_prefix+'/wave_recognize',
                         files={'wave_file':wf})
    text = html.text
    return text

if __name__ == '__main1__':
    print(wave_recognize_test())