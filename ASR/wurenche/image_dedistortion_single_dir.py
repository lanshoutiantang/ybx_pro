import cv2
import numpy as np
import os
import json



if __name__ == '__main__':

    # 数据目录
    data_path = r"D:\20241220_for_test_zhuqian_gaicheng"
    calib_file = ['CAM0.json', 'CAM4.json', 'CAM5.json', 'CAM6.json', 'CAM7.json']
    for root, dirs, files in os.walk(data_path):
        if os.path.basename(root).endswith('dedis'):
            continue
        for file in files:
            if file.lower().endswith('.jpg'):
                img_path = os.path.join(root, file)
                cam = os.path.basename(root)
                calib_path = os.path.join(data_path, 'calib', 'camera', cam + '.json')
                with open(calib_path, 'r') as f:
                    param = json.load(f)
                    intrinsic = param['intrinsic']
                    distortion = param['distortion']
                    # === 设置相机内参 ===
                    K = np.array([[intrinsic[0], intrinsic[1], intrinsic[2]],
                                  [intrinsic[3], intrinsic[4], intrinsic[5]],
                                  [intrinsic[6], intrinsic[7], intrinsic[8]]])
                    # K = np.array([[897.042243, 0.0, 638.676778],  # fx, 0, cx
                    #             [0.0, 896.649413, 361.291198],  # 0, fy, cy
                    #             [0, 0, 1]])                     # 0,  0,  1

                    # === 设置畸变系数 ===
                    D = np.array([distortion['k1'], distortion['k2'], distortion['p1'], distortion['p2'], distortion['k3']])
                    # D = np.array([-0.439723, 0.232219, -0.000379, 0.00017, -0.072481])  # [k1, k2, p1, p2, k3]

                # img_array = np.fromfile(img_path, dtype=np.uint8)
                # img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                img = cv2.imread(img_path)
                ##########################################################################################
                # # 计算新的相机内参矩阵
                # h, w = img.shape[:2]  # 获取图像宽高
                # new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(K, D, (w, h), 0.0, (w, h))

                # # 计算映射表
                # mapX, mapY = cv2.initUndistortRectifyMap(K, D, None, new_camera_matrix, (w, h), cv2.CV_32FC1)

                # # 进行去畸变
                # undistorted_img = cv2.remap(img, mapX, mapY, cv2.INTER_LINEAR)

                # # 保存去畸变后的图像
                # output_path = os.path.join(root[:-5] + '_dedis', os.path.basename(root), file)
                # if not os.path.exists(os.path.dirname(output_path)):
                #     os.makedirs(os.path.dirname(output_path))
                ##########################################################################################
                output_path = os.path.join(root[:-5] + '_undis', os.path.basename(root), file)
                if not os.path.exists(os.path.dirname(output_path)):
                    os.makedirs(os.path.dirname(output_path))
                ndistorted_img = cv2.undistort(img, K, D, None, K)
                cv2.imwrite(output_path, ndistorted_img)
                print("去畸变完成，保存为:", output_path)
