import numpy as np
import open3d as o3d
from PIL import Image



import os

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    alpha_x = 640 / 1280
    alpha_y = 352 / 720

    # 相机内参
    fx = 418.7097064794139 * alpha_x
    fy = 417.86560149071136 * alpha_y
    cx = 640.0659090919366 * alpha_x
    cy = 389.6926645506757 * alpha_y


    depth_path = r"D:\桌面\UBT\2025\双目\1.0.1\out_12121\test_1212\stereo_data_2442/1733922635.69915.png"

    # 读取深度图像（这里假设深度图是一个 numpy 数组）
    depth_image = Image.open(depth_path)
    depth_image = np.array(depth_image)

    # 获取图像的高度和宽度
    height, width = depth_image.shape

    points = []

    for v in range(height):
        for u in range(width):
            Z = depth_image[v, u] / 1000.0  # 获取深度值
            if Z == 0:  # 过滤掉无效的深度值
                continue
            # 计算点的三维坐标
            X = (u - cx) * Z / fx
            Y = (v - cy) * Z / fy
            points.append([X, Y, Z])
            # print(Z)
            # print([X, Y, Z])

    # 将点云转换为 NumPy 数组
    points = np.array(points)

    # 创建 Open3D 点云对象
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    # 显示点云
    vis = o3d.visualization.VisualizerWithVertexSelection()
    vis.create_window(window_name='Open3D', visible=True)
    vis.add_geometry(point_cloud)
    vis.run()
    point = vis.get_picked_points()
    vis.destroy_window()

    print(f"Selected {len(point)} points totally.")

    # # 可视化点云
    # axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])
    # o3d.visualization.draw_geometries([point_cloud, axis])
    #
    # # 将点云保存为 PCD 格式
    # o3d.io.write_point_cloud("output_point_cloud.pcd", point_cloud)