import os
import shutil
from pathlib import Path
import cv2
import yaml
import numpy as np
import bisect

# 时间差的最大容忍度，单位为秒（5ms）
MAX_TIME_DIFF = 0.08
DIS = 150
# 输入文件夹路径
left_dir  = f'/media/ubt-y/69691edc-a0ea-4b2f-9cb9-f79faf4a76de1/ros2/ros2bag_process/liuming_out/xiangzi/rosbag2_2025_02_20-11_51_20/left/'
right_dir = f'/media/ubt-y/69691edc-a0ea-4b2f-9cb9-f79faf4a76de1/ros2/ros2bag_process/liuming_out/xiangzi/rosbag2_2025_02_20-11_51_20/right/'

# 输出文件夹路径
output_dir = f'/home/ubt-y/workspace/stereo/联调性能验证/data_0224_remap/'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# 同步结果列表
synced_pairs = []

# 获取文件名并按时间戳排序
left_files = sorted([f for f in os.listdir(left_dir) if f.endswith('.png')], key=lambda x: float(x.split('.')[0]))
right_files = sorted([f for f in os.listdir(right_dir) if f.endswith('.png')], key=lambda x: float(x.split('.')[0]))

used_right_files = set()
last_matched_right_timestamp = -1

for left_file in left_files:
    left_timestamp = float(left_file.split('.')[0]) + float('0.' + left_file.split('.')[1])
    print(left_timestamp)
    best_match = None
    best_time_diff = float('inf')  # Initialize with a large number

    for right_file in right_files:
        if right_file in used_right_files:
            continue
        
        right_timestamp = float(right_file.split('.')[0]) + float('0.' + right_file.split('.')[1])
        
        if right_timestamp <= last_matched_right_timestamp:
            continue
        
        time_diff = abs(left_timestamp - right_timestamp)

        if time_diff <= MAX_TIME_DIFF and time_diff < best_time_diff:
            best_time_diff = time_diff
            best_match = right_file
    
    if best_match:
        used_right_files.add(best_match)
        last_matched_right_timestamp = float(best_match.split('.')[0])
        print(left_file)
        print(best_match)
        print("===========================")
        synced_pairs.append((left_file, best_match))
        
print(f"Total synced pairs: {len(synced_pairs)}")

# 去畸变函数
def LR_remap(imgLeft, imgRight, save_path, left_index, right_index,
             cameraMatrixL, distCoeffsL, 
             cameraMatrixR, distCoeffsR,
             R, T):
    
    imgL = cv2.imread(imgLeft)
    imgR = cv2.imread(imgRight)
    
    if imgL is None or imgR is None:
        print("img is None.")
        return
    
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
            cameraMatrixL, distCoeffsL, cameraMatrixR, distCoeffsR, grayL.shape[::-1], R, T)
    
    # 获取畸变矫正和极线对齐的映射矩阵
    mapL1, mapL2 = cv2.initUndistortRectifyMap(cameraMatrixL, distCoeffsL, R1, P1, [imgL.shape[1], imgL.shape[0]], cv2.CV_32FC1)
    mapR1, mapR2 = cv2.initUndistortRectifyMap(cameraMatrixR, distCoeffsR, R2, P2, [imgL.shape[1], imgL.shape[0]], cv2.CV_32FC1)
    
    # 应用映射矩阵进行畸变矫正和极线对齐
    rectifiedL = cv2.remap(imgL, mapL1, mapL2, cv2.INTER_CUBIC)
    rectifiedR = cv2.remap(imgR, mapR1, mapR2, cv2.INTER_CUBIC)
    
    # 使用索引命名文件
    # cv2.imwrite(os.path.join(save_path, f"{left_index:03d}_remapl.png"), rectifiedL)
    # cv2.imwrite(os.path.join(save_path, f"{right_index:03d}_remapr.png"), rectifiedR)
    
    rectifiedLR = cv2.hconcat([rectifiedL, rectifiedR])
    
    imgLeft = imgLeft.split("/")[-1]
    left_timestamp = float(imgLeft.split('.')[0]) + float('0.' + imgLeft.split('.')[1])
    
    cv2.imwrite(os.path.join(save_path, f"{left_timestamp}.png"), rectifiedLR)
    
    for i in range(10):
        start_point = (0, rectifiedLR.shape[0]//10 + i * rectifiedLR.shape[0]//10)
        end_point = (rectifiedLR.shape[1], rectifiedLR.shape[0]//10 + i * rectifiedLR.shape[0]//10)
        color = (0, 255, 0)
        thickness = 2
        
        rectifiedLR = cv2.line(rectifiedLR, start_point, end_point, color, thickness)

    cv2.imwrite(os.path.join(save_path, f"{left_index:03d}_val.png"), rectifiedLR)

    return rectifiedL, rectifiedR

def main():
    # 读取相机参数
    with open('/home/ubt-y/workspace/stereo/联调性能验证/rosbag_calib_0221-camchain.yaml', 'r') as file:
        loaded_params = yaml.safe_load(file) 
    
    alpha_w = 1.0
    alpha_h = 1.0
    # alpha_w = 0.9345
    # alpha_h = 0.9345
    
    distCoeffsL = np.array(loaded_params['cam0']['distortion_coeffs'])
    distCoeffsR = np.array(loaded_params['cam1']['distortion_coeffs'])
    cameraMatrixL = np.array([[loaded_params['cam0']['intrinsics'][0] * alpha_w, 0, loaded_params['cam0']['intrinsics'][2] * alpha_w],
                              [0, loaded_params['cam0']['intrinsics'][1] * alpha_h, loaded_params['cam0']['intrinsics'][3] * alpha_h],
                              [0,                                      0,                                      1]])
    cameraMatrixR = np.array([[loaded_params['cam1']['intrinsics'][0] * alpha_w, 0, loaded_params['cam1']['intrinsics'][2] * alpha_w],
                              [0, loaded_params['cam1']['intrinsics'][1] * alpha_h, loaded_params['cam1']['intrinsics'][3] * alpha_h],
                              [0,                                      0,                                      1]])
    RT_ = loaded_params['cam1']['T_cn_cnm1']
    RT_np = np.array(RT_)
    # RT_np = np.linalg.inv(RT_np)
    
    R = RT_np[:3, :3]
    T = RT_np[:3, 3]

    # 对所有同步的图像对进行去畸变处理
    for index, (left_file, right_file) in enumerate(synced_pairs):
        imgLeftPath = os.path.join(left_dir, left_file)
        imgRightPath = os.path.join(right_dir, right_file)
        LR_remap(imgLeft=imgLeftPath, imgRight=imgRightPath,
                 save_path=output_dir,
                 left_index=index,
                 right_index=index,
                 cameraMatrixL=cameraMatrixL,
                 distCoeffsL=distCoeffsL,
                 cameraMatrixR=cameraMatrixR,
                 distCoeffsR=distCoeffsR,
                 R=R,
                 T=T)

if __name__ == "__main__":
    main()