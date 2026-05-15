# import open3d as o3d
import os
import numpy as np
import pdb

# if __name__ == '__main__':
list = ["2023-09-08", "2023-10-07", "2023-11-10", "2023-11-13", "2023-11-16", "2024-02-29",
        "2024-04-10_car-0_hz0.5", "2024-05-13_bicycle_hz1", "2024-05-13_truck_hz0.5"]
for wenjainming in list:
    pcd_path = "/home/walker/mingliu/uautopilot_perception_bev_Test_v1.1.9/"+wenjainming+"/lidar"
    bin5_path = "/home/walker/mingliu/uautopilot_perception_bev_Test_v1.1.9/"+wenjainming+"/bin5"
    # print(pcd_path)
    # print(bin5_path)
    # pcd_path = "/home/walker/mingliu/uautopilot_perception_bev_Test_v1.1.9/2023-11-16/lidar"
    # bin5_path = "/home/walker/mingliu/uautopilot_perception_bev_Test_v1.1.9/2023-11-16/bin5"
    assert (bin5_path[-1] == "5")
    if not os.path.exists(bin5_path):
        os.makedirs(bin5_path)
    pcd_list = os.listdir(pcd_path)
    for pcd in pcd_list:
        pcd_file = os.path.join(pcd_path, pcd)
        save_file = os.path.join(bin5_path, pcd[:-3] + "bin")
        print("pcd: ", pcd)
        pcd_file = os.path.join(pcd_path, pcd)
        print("pcd_file: ", pcd_file)
        point_cloud = o3d.io.read_point_cloud(pcd_file)
        points = np.array(point_cloud.points)[:, :3].astype(np.float32)

        data = []
        for point in points:
            data.append([float(point[0]), float(point[1]), float(point[2]), float(1), float(0)])

        point_cloud = np.array(data, dtype=np.float32)
        # pdb.set_trace()

        point_cloud.tofile(save_file)
        print("PCD-->BIN5")

# cp -r ./2023-09-08/ ../uautopilot_perception_bev_Test_v1.1.10/2023-09-08/
# cp -r ./2023-10-07/ ../uautopilot_perception_bev_Test_v1.1.10/2023-10-07/
# cp -r ./2023-11-10/ ../uautopilot_perception_bev_Test_v1.1.10/2023-11-10/
# cp -r ./2023-11-13/ ../uautopilot_perception_bev_Test_v1.1.10/2023-11-13/
# cp -r ./2023-11-16/ ../uautopilot_perception_bev_Test_v1.1.10/2023-11-16/
# cp -r ./2024-02-29/ ../uautopilot_perception_bev_Test_v1.1.10/2024-02-29/
# cp -r ./2024-04-10_car-0_hz0.5/ ../uautopilot_perception_bev_Test_v1.1.10/2024-04-10_car-0_hz0.5/
# cp -r ./2024-05-13_bicycle_hz1/ ../uautopilot_perception_bev_Test_v1.1.10/2024-05-13_bicycle_hz1/
# cp -r ./2024-05-13_truck_hz0.5/ ../uautopilot_perception_bev_Test_v1.1.10/2024-05-13_truck_hz0.5/
