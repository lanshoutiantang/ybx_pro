import os

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")


if __name__ == '__main__':

    outer_path = r'D:\videoOutPicture'
    folderlist = os.listdir(outer_path)  # 列举文件夹
    print(folderlist)
    for folder in folderlist:
        inner_path = os.path.join(outer_path, folder)  # 获取子文件夹路径
        total_num_folder = len(folderlist)  # 子文件夹的总数
        filelist = os.listdir(inner_path)  # 列举子文件夹
        for folder_son in filelist:
            inner_son_path = os.path.join(inner_path, folder_son)  # 获取子子文件夹路径
            print(inner_son_path)
            filefilelist = os.listdir(inner_son_path)
            for folder_son_son in filefilelist:
                if folder_son_son.split(".")[1] == "png":
                    continue

                inner_son_son_path = os.path.join(inner_son_path, folder_son_son)


                # 读取点云
                ply = o3d.io.read_point_cloud(inner_son_son_path)

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
