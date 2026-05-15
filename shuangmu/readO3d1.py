import os

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':


    outer_path = r'D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian2\out3 - 副本\group_09'
    folderlist = os.listdir(outer_path)  # 列举文件夹
    print(folderlist)
    for folder in folderlist:
        inner_path = os.path.join(outer_path, folder)  # 获取子文件夹路径
        if folder.split(".")[1] == "png":
            continue


        # 读取点云
        ply = o3d.io.read_point_cloud(inner_path)

        print(folder)
        # 获取点云的z轴坐标
        points = np.asarray(ply.points)
        z_values = points[:, 2]

        # 将z轴值归一化到[0, 1]范围
        z_min = np.min(z_values)
        z_max = np.max(z_values)
        z_normalized = (z_values - z_min) / (z_max - z_min)

        # 生成颜色映射
        colormap = plt.get_cmap("viridis")  # 可以选择其他颜色映射，如 'plasma', 'inferno', 'magma', etc.
        colors = colormap(z_normalized)[:, :3]  # 取前三个通道 (RGB)

        # 将颜色赋值给点云
        # ply.colors = o3d.utility.Vector3dVector(colors)

        # 显示点云
        vis = o3d.visualization.VisualizerWithVertexSelection()
        vis.create_window(window_name='Open3D', visible=True)
        vis.add_geometry(ply)
        vis.run()
        point = vis.get_picked_points()
        vis.destroy_window()

        print(f"Selected {len(point)} points totally.")
