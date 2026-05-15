import os
import numpy as np
import cv2
from pathlib import Path
from tqdm import tqdm

def write_point_cloud(ply_filename, points):
    formatted_points = []
    for point in points:
        formatted_points.append("%f %f %f\n" % (point[0], point[1], point[2]))

    with open(ply_filename, "w") as out_file:
        out_file.write('''ply
format ascii 1.0
element vertex %d
property float x
property float y
property float z
end_header
%s
''' % (len(points), "".join(formatted_points)))

def depth_image_to_point_cloud(depth, scale, K, pose):
    u = range(0, depth.shape[1])
    v = range(0, depth.shape[0])

    u, v = np.meshgrid(u, v)
    u = u.astype(float)
    v = v.astype(float)

    Z = depth.astype(float) / scale
    X = (u - K[0, 2]) * Z / K[0, 0]
    Y = (v - K[1, 2]) * Z / K[1, 1]

    X = np.ravel(X)
    Y = np.ravel(Y)
    Z = np.ravel(Z)

    valid = Z > 0

    X = X[valid]
    Y = Y[valid]
    Z = Z[valid]

    position = np.vstack((X, Y, Z, np.ones(len(X))))
    position = np.dot(pose, position)

    points = np.transpose(position[0:3, :]).tolist()

    return points

def build_point_cloud(dataset_path, scale, view_ply_in_world_coordinate):
    # 内参矩阵

    # K = [[fx,  0,  cx],
    #     [0,   fy,  cy],
    #     [0,    0,   1]]
    K = np.array([
        [428.7624450161, 0.0, 625.2238311767578],
        [0.0, 428.7624450161, 448.9012031555176],
        [0.0, 0.0, 1.0]
    ])
    #K = np.array([
    #    [779.50272290593239, 0.0, 969.85623168945312],
    #    [0.0, 779.50272290593239, 785.06515502929688],
    #    [0.0, 0.0, 1.0]
    #])

    # 修正路径逻辑：直接处理dataset_path下的所有.png（假设depth图直接放在该路径下）
    # 如果depth图在子目录"depth_filter"，则用下面一行替换
    # depth_maps_path = Path(dataset_path) / "depth_filter"
    depth_maps_path = Path(dataset_path)
    
    # 批量搜索所有.png文件（包括子目录，如需仅当前目录则去掉recursive=True）
    depth_files = sorted(depth_maps_path.glob('**/*.png'))  # **表示递归子目录

    if not depth_files:
        print(f"警告：在路径 {depth_maps_path} 下未找到任何.png文件")
        return

    # 位姿处理

    
    if view_ply_in_world_coordinate:
        # 示例位姿（根据实际情况修改）
        poses = np.array([
            [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]],
        ])
        # 复制位姿以匹配所有图像数量
        poses = np.repeat(poses, len(depth_files), axis=0) if len(depth_files) > 1 else poses
    else:
        poses = np.tile(np.eye(4), (len(depth_files), 1, 1))  # 每个图像用单位矩阵

    # 创建输出目录
    save_ply_path = Path(dataset_path) / "point_clouds"
    save_ply_path.mkdir(exist_ok=True)

    # 批量处理所有深度图
    for i, depth_file in enumerate(tqdm(depth_files, desc="处理深度图")):
        # 读取深度图
        depth = cv2.imread(str(depth_file), cv2.IMREAD_UNCHANGED)
        if depth is None:
            print(f"跳过无法读取的文件: {depth_file}")
            continue

        # 转换为点云
        if view_ply_in_world_coordinate:
            current_points_3D = depth_image_to_point_cloud(depth, scale, K, poses[i])
        else:
            current_points_3D = depth_image_to_point_cloud(depth, scale, K, poses[i])
        
        # 保存PLY文件（保持原文件目录结构）
        relative_path = depth_file.relative_to(depth_maps_path)
        ply_save_dir = save_ply_path / relative_path.parent
        ply_save_dir.mkdir(parents=True, exist_ok=True)
        save_ply_name = ply_save_dir / f"{depth_file.stem}.ply"
        write_point_cloud(str(save_ply_name), current_points_3D)

if __name__ == '__main__':
    # 批量处理的路径列表（替换为你的实际路径）
    dataset_paths = [
        # r"D:\yungu_1216\1215_dark_grey_45_0.7_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_45_1_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_45_1.5_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_45_2_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_60_0.7_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_60_1_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_60_1.5_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_60_2_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_75_0.7_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_75_1_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_75_1.5_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_75_2_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_90_0.7_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_90_1_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_90_1.5_used\depth",
        # r"D:\yungu_1216\1215_dark_grey_90_2_used\depth",
        # r"D:\yungu_1216\1216_dark_black_45_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_black_45_1_used\depth",
        # r"D:\yungu_1216\1216_dark_black_45_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_black_45_2_used\depth",
        # r"D:\yungu_1216\1216_dark_black_60_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_black_60_1_used\depth",
        # r"D:\yungu_1216\1216_dark_black_60_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_black_60_2_used\depth",
        # r"D:\yungu_1216\1216_dark_black_75_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_black_75_1_used\depth",
        # r"D:\yungu_1216\1216_dark_black_75_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_black_75_2_used\depth",
        # r"D:\yungu_1216\1216_dark_black_90_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_black_90_1_used\depth",
        # r"D:\yungu_1216\1216_dark_black_90_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_black_90_2_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_45_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_45_1_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_45_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_45_2_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_60_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_60_1_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_60_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_60_2_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_75_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_75_1_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_75_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_75_2_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_90_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_90_1_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_90_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_blue_90_2_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_45_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_45_1_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_45_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_45_2_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_60_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_60_1_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_60_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_60_2_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_75_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_75_1_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_75_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_75_2_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_90_0.7_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_90_1_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_90_1.5_used\depth",
        # r"D:\yungu_1216\1216_dark_grey_90_2_used\depth"
        # 可继续添加其他路径...
        r"C:\Users\ubtech\Desktop\ceshi_0916_used\depth"
    ]
    
    # 配置参数
    view_ply_in_world_coordinate = False  # 相机坐标系
    scale_factor = 1000.0  # 深度图尺度因子
    
    # 遍历所有路径批量处理
    for dataset_path in dataset_paths:
        path_obj = Path(dataset_path)
        if not path_obj.exists():
            print(f"跳过不存在的路径: {dataset_path}")
            continue
        
        print(f"\n开始处理数据集: {dataset_path}")
        print(f"内参矩阵:\n{np.array([[428.73, 0.0, 625], [0.0, 428.76, 448.9], [0.0, 0.0, 1.0]])}")
        print(f"深度尺度因子: {scale_factor}")
        print(f"坐标系: {'世界坐标系' if view_ply_in_world_coordinate else '相机坐标系'}")
        
        build_point_cloud(dataset_path, scale_factor, view_ply_in_world_coordinate)
    
    print("\n所有数据集处理完成！")