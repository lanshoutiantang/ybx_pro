import speech_recognition as sr

import subprocess
import ffmpeg

def video_to_text(input_video_path, output_text_path):
    """
    使用FFmpeg将视频文件转换为文本。
    这里使用的是FFmpeg的`ocr`文本识别功能。
    """
    command = [
        'ffmpeg',
        '-i', input_video_path,  # 输入视频文件
        '-filter_complex', 'ocr=lang=chi_sim',  # 使用OCR，设置语言为简体中文
        '-f', 'text', output_text_path  # 输出文本文件
    ]

    try:
        subprocess.run(command, check=True)
        print(f"视频转换为文本成功: {output_text_path}")
    except subprocess.CalledProcessError as e:
        print(f"视频转换为文本失败: {e}")


# 使用示例
# video_to_text('input_video.mp4', 'output_text.txt')

if __name__ == '__main__':
    # # 使用默认的麦克风作为音频源（如果需要从文件读取，可以使用sr.AudioFileClip(audio_file)）
    # r = sr.Recognizer()
    # audio_output_path = r'D:\Program Files\JetBrains\pythonProject\my.wav'
    # # 识别音频文件（这里假设你已经将视频转换为音频并保存为文件）
    # with sr.AudioFile(audio_output_path) as source:
    #     audio_data = r.record(source)
    #     text = r.recognize_google(audio_data, language="zh-CN")  # 使用谷歌语音识别服务，并指定语言为中文（简体）
    #     print(text)  # 输出识别结果
    # 使用示例
    video_to_text(r'D:\Program Files\JetBrains\pythonProject\my.mp3', r'D:\Program Files\JetBrains\pythonProject\output_text.txt')
