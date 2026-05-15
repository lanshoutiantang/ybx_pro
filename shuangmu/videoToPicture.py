import cv2
import os


def extract_frames_from_video(video_path, start_time, end_time, output_folder, frame_interval=1):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 获取视频的帧率
    fps = cap.get(cv2.CAP_PROP_FPS)
    # liuming 1s抽1帧
    fps = 1

    # 计算起始帧和结束帧
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # 设置视频读取的起始位置
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    current_frame = start_frame
    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        # 保存帧到指定文件夹
        if (current_frame - start_frame) % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{current_frame:06d}.png")
            cv2.imwrite(frame_filename, frame)

        current_frame += 1

    # 释放视频捕获对象
    cap.release()
    cv2.destroyAllWindows()


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")


if __name__ == '__main__':
    # # 示例使用
    # video_path = r'D:\video\20241016-150613 (1).mp4'  # 视频文件
    # output_folder = r'D:\videoOut'  # 图像保存目录
    # start_time = 0  # 起始时间（秒）
    # end_time = 10  # 结束时间（秒）
    #
    # extract_frames_from_video(video_path, start_time, end_time, output_folder)

    # 示例使用
    start_time = 0  # 起始时间（秒）
    end_time = 15  # 结束时间（秒）

    outer_path = r'D:\video'
    output_folder = r'D:\videoOut'  # 图像保存目录
    folderlist = os.listdir(outer_path)  # 列举文件夹
    create_folder_if_not_exists(output_folder)  # 图像输出目录
    print(folderlist)
    for folder in folderlist:
        inner_path = os.path.join(outer_path, folder)  # 获取子文件夹路径
        total_num_folder = len(folderlist)  # 子文件夹的总数
        filelist = os.listdir(inner_path)  # 列举子文件夹
        outer_son_path = os.path.join(output_folder, folder)  # 获取子输出文件夹路径
        create_folder_if_not_exists(outer_son_path)  # 图像输出子目录
        for folder_son in filelist:
            inner_son_path = os.path.join(inner_path, folder_son)  # 获取子子文件夹路径
            print(folder_son)
            outer_son_son_path = os.path.join(output_folder, folder, folder_son)  # 获取子子输出文件夹路径
            create_folder_if_not_exists(outer_son_son_path)  # 图像输出子子目录
            extract_frames_from_video(inner_son_path, start_time, end_time, outer_son_son_path)
