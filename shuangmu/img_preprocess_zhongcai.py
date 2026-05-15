import cv2
import numpy as np
import yaml
import os


def undistort_frame(frame, camera_matrix, dist_coeffs, R1, P1):
    """  
    使用相机内参和畸变系数来校正帧  
    """
    map1, map2 = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, R1, P1, [frame.shape[1], frame.shape[0]],
                                             cv2.CV_32FC1)
    # mapR1, mapR2 = cv2.initUndistortRectifyMap(cameraMatrixR, distCoeffsR, R2, P2, [imgL.shape[1], imgL.shape[0]], cv2.CV_32FC1)

    # 应用映射矩阵进行畸变矫正和极线对齐
    rectified = cv2.remap(frame, map1, map2, cv2.INTER_CUBIC)
    # rectifiedR = cv2.remap(imgR, mapR1, mapR2, cv2.INTER_CUBIC)

    return rectified


def read_imgs(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load {image_path}")

    _, width = image.shape[:2]

    center_x = width // 2

    # 7. 分割图像为左右两部分
    left_image = image[:, :center_x]
    right_image = image[:, center_x:]

    return left_image, right_image


def main():
    with open('camera_params_2024-09-25-11-28-07.yaml', 'r') as file:
        loaded_params = yaml.safe_load(file)

        camera_matrix_l = np.array(loaded_params["cameraMatrixL"])
        dist_coeffs_l = np.array(loaded_params["distCoeffsL"])
        R1_l = np.array(loaded_params["R1"])
        P1_l = np.array(loaded_params["P1"])

        camera_matrix_r = np.array(loaded_params["cameraMatrixR"])
        dist_coeffs_r = np.array(loaded_params["distCoeffsR"])
        R1_r = np.array(loaded_params["R2"])
        P1_r = np.array(loaded_params["P2"])

    input_folder = r'D:\shijihe-xieshi-30cm.mp4'
    output_folder = r'D:\shijihe-xieshi-30cm.mp4_'

    os.makedirs(output_folder, exist_ok=True)

    for filename in sorted(os.listdir(input_folder)):
        image_path = os.path.join(input_folder, filename)
        frame_left, frame_right = read_imgs(image_path)

        frame_left = undistort_frame(frame_left, camera_matrix_l, dist_coeffs_l, R1_l, P1_l)
        frame_right = undistort_frame(frame_right, camera_matrix_r, dist_coeffs_r, R1_r, P1_r)

        # 将左右图像帧拼接
        combined_frame = cv2.hconcat([frame_left, frame_right])

        bright_image = combined_frame.astype(np.float32) * 1.0
        bright_image = np.clip(bright_image, 0, 255).astype(np.uint8)

        out_img_path = os.path.join(output_folder, filename)

        # 显示拼接后的图像帧
        cv2.imwrite(out_img_path, bright_image)
        print(out_img_path)


if __name__ == '__main__':
    main()
