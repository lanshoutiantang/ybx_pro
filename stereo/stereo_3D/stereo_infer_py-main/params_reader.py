import configparser
import cv2
import numpy as np


def read_stereo_params(stereo_params_path):
    fs = cv2.FileStorage(stereo_params_path, cv2.FILE_STORAGE_READ)

    if not fs.isOpened():
        raise ValueError(f"无法打开文件: {stereo_params_path}")

    # 读取 P1 矩阵 (3x4)
    p1 = fs.getNode("P1").mat()

    # 确保 P1 是 3x4 的矩阵
    if p1 is None or p1.shape != (3, 4):
        raise ValueError("P1 矩阵格式错误，应为 3x4")

    # 提取前 3 列作为内参矩阵 (3x3)
    K_stereo = p1[:, :3]

    fs.release()
    return K_stereo


def read_all_stereo_params(stereo_params_path):
    fs = cv2.FileStorage(stereo_params_path, cv2.FILE_STORAGE_READ)

    if not fs.isOpened():
        raise ValueError(f"无法打开文件: {stereo_params_path}")

    # 读取 P1 矩阵 (3x4)
    p1 = fs.getNode("P1").mat()

    # 确保 P1 是 3x4 的矩阵
    if p1 is None or p1.shape != (3, 4):
        raise ValueError("P1 矩阵格式错误，应为 3x4")

    # 提取前 3 列作为内参矩阵 (3x3)
    K_stereo = p1[:, :3]

    params = {}
    params["K_stereo"] = K_stereo
    params["K1"] = fs.getNode("K1").mat()
    params["D1"] = fs.getNode("D1").mat()
    params["K2"] = fs.getNode("K2").mat()
    params["D2"] = fs.getNode("D2").mat()
    params["R"] = fs.getNode("R").mat()
    params["T"] = fs.getNode("T").mat()
    params["E"] = fs.getNode("E").mat()
    params["F"] = fs.getNode("F").mat()
    params["image_size"] = fs.getNode("size").mat()
    if not fs.getNode("alpha_stereo_rectify").empty():
        params["alpha_stereo_rectify"] = fs.getNode("alpha_stereo_rectify").real()

    fs.release()
    return params


def read_mech_params(mech_params_path):
    fs = cv2.FileStorage(mech_params_path, cv2.FILE_STORAGE_READ)

    texture_camera_matrix = fs.getNode("texture_camera_matrix").mat()
    texture_distortion = fs.getNode("texture_distortion").mat()
    depth_camera_matrix = fs.getNode("depth_camera_matrix").mat()
    depth_distortion = fs.getNode("depth_distortion").mat()
    r_from_depth_to_texture = fs.getNode("r_from_depth_to_texture").mat()
    t_from_depth_to_texture = fs.getNode("t_from_depth_to_texture").mat()
    fs.release()

    return (
        texture_camera_matrix,
        texture_distortion,
        depth_camera_matrix,
        depth_distortion,
        r_from_depth_to_texture,
        t_from_depth_to_texture,
    )


def read_gemini_params_from_ini(ini_path):
    """
    从INI文件中读取相机参数并转换为OpenCV格式

    参数:
        ini_path (str): INI文件路径

    返回:
        dict: 包含Color和Depth相机参数的字典，每个都包含:
            - 'camera_matrix': OpenCV格式的3x3相机内参矩阵
            - 'dist_coeffs': OpenCV格式的畸变系数矩阵
    """
    config = configparser.ConfigParser()
    config.read(ini_path)

    params = {"Color": {}, "Depth": {}}

    # 处理Color相机参数
    if "ColorIntrinsic" in config and "ColorDistortion" in config:
        # 内参矩阵
        fx = float(config["ColorIntrinsic"]["fx"])
        fy = float(config["ColorIntrinsic"]["fy"])
        cx = float(config["ColorIntrinsic"]["cx"])
        cy = float(config["ColorIntrinsic"]["cy"])

        camera_matrix = np.array(
            [[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64
        )
        params["Color"]["camera_matrix"] = camera_matrix

        # 畸变系数 (k1, k2, p1, p2, k3, k4, k5, k6)
        # OpenCV通常使用 (k1, k2, p1, p2, k3) 或 (k1, k2, p1, p2, k3, k4, k5, k6)
        dist_coeffs = np.array(
            [
                float(config["ColorDistortion"]["k1"]),
                float(config["ColorDistortion"]["k2"]),
                float(config["ColorDistortion"]["p1"]),
                float(config["ColorDistortion"]["p2"]),
                float(config["ColorDistortion"]["k3"]),
                float(config["ColorDistortion"]["k4"]),
                float(config["ColorDistortion"]["k5"]),
                float(config["ColorDistortion"]["k6"]),
            ],
            dtype=np.float64,
        )
        params["Color"]["dist_coeffs"] = dist_coeffs

    # 处理Depth相机参数
    if "DepthIntrinsic" in config and "DepthDistortion" in config:
        # 内参矩阵
        fx = float(config["DepthIntrinsic"]["fx"])
        fy = float(config["DepthIntrinsic"]["fy"])
        cx = float(config["DepthIntrinsic"]["cx"])
        cy = float(config["DepthIntrinsic"]["cy"])

        camera_matrix = np.array(
            [[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64
        )
        params["Depth"]["camera_matrix"] = camera_matrix

        # 畸变系数
        dist_coeffs = np.array(
            [
                float(config["DepthDistortion"]["k1"]),
                float(config["DepthDistortion"]["k2"]),
                float(config["DepthDistortion"]["p1"]),
                float(config["DepthDistortion"]["p2"]),
                float(config["DepthDistortion"]["k3"]),
                float(config["DepthDistortion"]["k4"]),
                float(config["DepthDistortion"]["k5"]),
                float(config["DepthDistortion"]["k6"]),
            ],
            dtype=np.float64,
        )
        params["Depth"]["dist_coeffs"] = dist_coeffs

    return params


def test_read_stereo_params():
    stereo_params_path = (
        "/media/ubt/data/head/_calib_files/20250529_Faraday_02_params/stereo_cam.yml"
    )
    K_stereo = read_stereo_params(stereo_params_path)
    print("K_stereo:\n", K_stereo)


def test_read_mech_params():
    mech_params_path = "/media/ubt/data/head/_calib_files/suite002_mech_params.yml"
    (
        texture_camera_matrix,
        texture_distortion,
        depth_camera_matrix,
        depth_distortion,
        r_from_depth_to_texture,
        t_from_depth_to_texture,
    ) = read_mech_params(mech_params_path)

    print("Texture Camera Matrix:\n", texture_camera_matrix)
    print("Texture Distortion Coefficients:\n", texture_distortion)
    print("Depth Camera Matrix:\n", depth_camera_matrix)
    print("Depth Distortion Coefficients:\n", depth_distortion)
    print("Rotation from Depth to Texture Camera:\n", r_from_depth_to_texture)
    print("Translation from Depth to Texture Camera:\n", t_from_depth_to_texture)


def test_read_gemini_params():
    Gemini_params_path = "/media/ubt/data/head/_calib_files/suite002_Gemini_CameraParam_Orbbec Gemini 2 LAY8H641003V_Color1280x800_Depth1280x800.ini"
    params = read_gemini_params_from_ini(Gemini_params_path)

    print("Color Camera Matrix:")
    print(params["Color"]["camera_matrix"])
    print("\nColor Distortion Coefficients:")
    print(params["Color"]["dist_coeffs"])

    print("\nDepth Camera Matrix:")
    print(params["Depth"]["camera_matrix"])
    print("\nDepth Distortion Coefficients:")
    print(params["Depth"]["dist_coeffs"])


if __name__ == "__main__":
    # test_read_stereo_params()
    # test_read_mech_params()
    test_read_gemini_params()
