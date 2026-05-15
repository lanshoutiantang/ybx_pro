import cv2
import numpy as np
import os

DEBUG = False  # 是否开启调试模式

if DEBUG:
    import open3d as o3d


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

    fs.release()
    return params


def scale_crop_intrinsic_old_sensing(K_stereo):
    fx = K_stereo[0, 0]
    fy = K_stereo[1, 1]
    cx = K_stereo[0, 2] - 160
    cy = K_stereo[1, 2] - 144

    K_cropped = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
    return K_cropped


def scale_crop_intrinsic_new_sensing(K_stereo):
    fx = K_stereo[0, 0] * 0.5
    fy = K_stereo[1, 1] * 0.5
    cx = K_stereo[0, 2] * 0.5
    cy = K_stereo[1, 2] * 0.5 - 144

    K_cropped = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
    return K_cropped


def depth_to_ply(depth_image, K, roi=None):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    height, width = depth_image.shape

    # 处理 ROI
    if roi is not None:
        x0, y0, w, h = roi
        depth_image = depth_image[y0 : y0 + h, x0 : x0 + w]
        u, v = np.meshgrid(np.arange(x0, x0 + w), np.arange(y0, y0 + h))
    else:
        u, v = np.meshgrid(np.arange(width), np.arange(height))

    z = depth_image.astype(np.float32)
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy

    points = np.stack((x, y, z), axis=-1).reshape(-1, 3)

    # 过滤掉无效点（z==0）
    valid = (z > 0).reshape(-1)
    points = points[valid]

    return points


def fit_plane_least_squares(points):
    """
    使用最小二乘法拟合平面 z = ax + by + c
    返回平面法向量和常数项 d，使得 n·p + d = 0
    """
    # 拆分 x, y, z
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]

    # 构建 A·[a, b, c]^T ≈ z
    A = np.c_[x, y, np.ones_like(x)]
    coeff, _, _, _ = np.linalg.lstsq(A, z, rcond=None)  # 求解 ax + by + c ≈ z

    a, b, c = coeff

    # 将 z = ax + by + c 转换为 Ax + By + Cz + D = 0
    # => a*x + b*y - z + c = 0 → normal = [a, b, -1], d = c
    normal = np.array([a, b, -1.0])
    norm = np.linalg.norm(normal)
    normal /= norm  # 单位化
    d = c / norm

    return normal, d


def visualize_point_cloud(points):
    """
    使用 Open3D 可视化点云
    参数:
        points: Nx3 numpy array，点云数据
    """
    # 创建 Open3D 点云对象
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # 可视化
    o3d.visualization.draw_geometries([pcd])


def compute_center_roi(width, height, ratio=0.8):
    roi_width = int(ratio * width)
    roi_height = int(ratio * height)
    x = (width - roi_width) // 2
    y = (height - roi_height) // 2
    return (x, y, roi_width, roi_height)


def compute_point_to_plane_distances(points, normal, d):
    # 点积 Ax + By + Cz + D
    distances = np.abs(points @ normal + d)
    # distances = np.abs(np.dot(points, normal) + d) / np.linalg.norm(normal)
    std_dev = np.std(distances)
    return distances, std_dev


def compute_depth_precision(depths, roi):
    x, y, w, h = roi
    N = len(depths)
    assert N > 1, "需要至少两张深度图"

    # 提取 ROI 并堆成 3D 数组
    roi_stack = np.stack(
        [d[y : y + h, x : x + w].astype(np.float32) for d in depths], axis=0
    )

    # 计算逐像素标准差
    std_map = np.std(roi_stack, axis=0)

    # 排除无效点（如深度为 0）
    valid_mask = np.all(roi_stack > 0, axis=0)  # 所有帧都大于 0 的位置
    mean_fluctuation = np.mean(std_map[valid_mask]) if np.any(valid_mask) else 0.0

    return std_map, mean_fluctuation


if __name__ == "__main__":
    # settings
    current_dir = os.path.dirname(os.path.abspath(__file__))
    stereo_params_path = "your_stereo_cam.yml"
    depth_folder = "your_whitewall_data_folder"
    reference_distance = 500  # mm

    roi_ratio = 0.4  # 使用 40% 的ROI区域来计算指标
    min_depth_num = 5  # 最小所需深度图像数量

    use_new_sensing = True  # 如果使用的是新森云相机就设置为True,否则设置为False
    depth_shape = (576, 960)

    # read all depths
    depths = []
    for file in os.listdir(depth_folder):
        if not file.endswith(".png"):
            continue

        depth_path = os.path.join(depth_folder, file)
        depth = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
        if depth is not None:
            depths.append(depth)

    # check boundary
    num_depths = len(depths)
    if num_depths < min_depth_num:
        raise ValueError(f"深度图像({num_depths})数量不足")
    if depths[0].shape != depth_shape:
        raise ValueError(f"深度图像尺寸错误: {depths[0].shape}")
    height, width = depths[0].shape

    # calculating
    params = read_all_stereo_params(stereo_params_path)
    if DEBUG:
        print("Stereo Camera Parameters:")
        print(params["K_stereo"])
    K_stereo = params["K_stereo"]
    K_cropped = scale_crop_intrinsic_old_sensing(K_stereo)
    if use_new_sensing:
        K_cropped = scale_crop_intrinsic_new_sensing(K_stereo)

    # convert depth to point cloud
    points_all = []
    roi = compute_center_roi(width, height, ratio=roi_ratio)
    for depth in depths:
        points = depth_to_ply(depth, K_cropped, roi)
        points_all.append(points)
    points_all = np.vstack(points_all)

    if DEBUG:
        visualize_point_cloud(points_all)

    normal, d = fit_plane_least_squares(points)
    if DEBUG:
        print(
            f"拟合平面方程: {normal[0]:.4f}x + {normal[1]:.4f}y + {normal[2]:.4f}z + {d:.4f} = 0"
        )

    print(f"{reference_distance=:.2f} mm")

    # accuracy
    accuracy = np.abs(d) - reference_distance
    print(f"{accuracy=:.2f} mm")
    print(f"accuracy_relative={accuracy / reference_distance:.2%}")

    # spatial_noise
    distances, std_dev = compute_point_to_plane_distances(points_all, normal, d)
    spatial_noise = std_dev
    print(f"{spatial_noise=:.2f} mm")
    print(f"spatial_noise_relative={spatial_noise / reference_distance:.2%}")

    # precision
    std_map, mean_fluctuation = compute_depth_precision(depths, roi)
    precision = mean_fluctuation
    print(f"{precision=:.2f} mm")
    print(f"precision_relative={precision / reference_distance:.2%}")
