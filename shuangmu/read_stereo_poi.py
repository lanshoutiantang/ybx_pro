import os

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt



if __name__ == '__main__':
    # 读取点云

    outer_path = r'D:\compare_rgbd\inside'
    folderlist = os.listdir(outer_path)  # 列举文件夹
    print(folderlist)
    for folder in folderlist:
        inner_path = os.path.join(outer_path, folder)  # 获取子文件夹路径
        if folder.split(".")[-1] == "png":
            continue

        print(inner_path)
        ply = o3d.io.read_point_cloud(inner_path)

        # 显示点云
        vis = o3d.visualization.VisualizerWithVertexSelection()
        # vis = o3d.visualization.VisualizerWithEditing()
        vis.create_window(window_name='Open3D', visible=True)
        # 将原点添加到可视化器中
        # vis.add_geometry(origin_sphere)
        vis.add_geometry(ply)
        vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0))
        vis.run()
        point = vis.get_picked_points()
        vis.destroy_window()

        print(f"Selected {len(point)} points totally.")


