import numpy as np
import open3d as o3d
import cv2
import yaml


def depth_to_point_cloud(depth_map, K):
    f_x, f_y = K[0, 0], K[1, 1]
    c_x, c_y = K[0, 2], K[1, 2]
    points = []

    h, w = depth_map.shape
    for v in range(h):
        for u in range(w):
            Z = depth_map[v, u] /1000
            if Z == 0:  # Skip invalid depth
                continue
            X = (u - c_x) * Z / f_x
            Y = (v - c_y) * Z / f_y
            points.append((X, Y, Z))

    return np.asarray(points)

def transform_point_cloud(points, T):
    transformed_points = []
    for point in points:
        X, Y, Z = point
        homogeneous_point = np.array([X, Y, Z, 1])
        transformed_point = T @ homogeneous_point
        transformed_points.append(transformed_point[:3])
    
    return np.asarray(transformed_points)



if __name__ == '__main__':

    left_pcd = r'D:\compare_rgbd\outside_1\1730289553.12161.ply'
    rgbd_png = r'D:\compare_rgbd\outside_1\1730289553.12161.png'

    # 输入数据
    depth_map = cv2.imread(rgbd_png, cv2.IMREAD_ANYDEPTH) # 深度图
    left_camera_points = o3d.io.read_point_cloud(left_pcd) # 左目相机点云
    left_camera_points = np.asarray(left_camera_points.points, dtype=np.float64)

    with open('D:\Program Files\JetBrains\pythonProject\shuangmu\camchain-homecodecalibrstereo_matchingstereo_left_2_head_rgbd.yaml', 'r') as file:
        loaded_params = yaml.safe_load(file)

    # K_rgbd = np.array([[loaded_params['cam1']['intrinsics'][0], 0, loaded_params['cam1']['intrinsics'][2]],
    #                 [0, loaded_params['cam1']['intrinsics'][1], loaded_params['cam1']['intrinsics'][3]],
    #                 [0, 0, 1]])   # RGB-D 相机内参矩阵
    K_rgbd = np.array([[305.70281982421875, 0, 315.812744140625],
                       [0, 305.96868896484375, 199.7202911376953],
                       [0, 0, 1]])   # RGB-D 相机内参矩阵
    T = np.array(loaded_params['cam1']['T_cn_cnm1'])
    T = np.linalg.inv(T)

    # 转换深度图为点云并投影
    rgbd_points = depth_to_point_cloud(depth_map, K_rgbd)
    transformed_points = transform_point_cloud(rgbd_points, T)

    # 使用 Open3D 进行点云比较
    pcd_left = o3d.geometry.PointCloud()
    pcd_left.points = o3d.utility.Vector3dVector(left_camera_points)

    pcd_transformed = o3d.geometry.PointCloud()
    pcd_transformed.points = o3d.utility.Vector3dVector(transformed_points)

    pcd_left.paint_uniform_color([0, 0, 1])  # 红色
    pcd_transformed.paint_uniform_color([0, 1, 0])  # 绿色

    o3d.visualization.draw_geometries([pcd_left, pcd_transformed])
    # # o3d.visualization.draw_geometries([pcd_left])

    # vis = o3d.visualization.VisualizerWithVertexSelection()
    # # vis = o3d.visualization.VisualizerWithEditing()
    # vis.create_window(window_name='Open3D', visible=True)
    # # 将原点添加到可视化器中
    # # vis.add_geometry(origin_sphere)
    # vis.add_geometry(pcd_left)
    # vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0))
    # vis.run()
    # point = vis.get_picked_points()
    # vis.destroy_window()