import os
import cv2
import numpy as np
from pathlib import Path

# Settings
output_vis_dir = (
    "/media/ubt/data/head/20260120_fenjian/sanyi_04_val/temp_result_s0.1.5_0/vis_dir"
)
images_dir = "/media/ubt/data/head/20260120_fenjian/sanyi_04_val/temp_result_s0.1.5_0/stereo_depth/rgb"
labels_dir = (
    "/media/ubt/data/head/20260120_fenjian/sanyi_04_val/temp_result_s0.1.5_0/labels_960"
)
poses_dir = "/media/ubt/data/head/20260120_fenjian/sanyi_04_val/poses"

output_dir = output_vis_dir

os.makedirs(output_dir, exist_ok=True)

# # resolution_mode = 0
# fx = 388.6014963549259
# fy = 388.6014963549259
# cx = 480.0
# cy = 240.0

# resolution_mode = 1. use ROI
fx = 777.20299270985186
fy = 777.20299270985186
cx = 480.0
cy = 288.0

k_vector = np.array([fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0])
K = k_vector.reshape(3, 3)


def read_poses_from_file(file_path):
    poses = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # 跳过空行和注释
                continue
            values = list(map(float, line.split()))
            if len(values) != 13:
                raise ValueError(
                    f"Invalid line: {line}. Expected 12 values, got {len(values)}"
                )
            # 构建旋转矩阵 (3x3)
            R = np.array(values[4:], dtype=np.float32).reshape(3, 3)
            t = np.array(values[1:4], dtype=np.float32).reshape(3, 1)

            # 构造 4x4 的齐次变换矩阵
            pose_matrix = np.zeros((4, 4), dtype=np.float32)
            pose_matrix[:3, :3] = R  # 填充旋转矩阵
            pose_matrix[:3, 3] = t.flatten()  # 填充平移向量（注意展平为一维）
            pose_matrix[3, 3] = 1  # 右下角设置为 1

            label = values[0]

            if label == 99:
                print("!!!!!!!!")
                continue

            poses.append(pose_matrix)

    return poses


def get_axis(
    T,
):
    R = T[:3, :3]
    t = T[:3, 3]

    # 计算物体坐标系的原点和轴端点
    O_cam = t
    L = 0.1  # 轴的长度，可以根据需要调整
    X_axis_dir = R[:, 0]
    Y_axis_dir = R[:, 1]
    Z_axis_dir = R[:, 2]

    X_end_cam = O_cam + L * X_axis_dir
    Y_end_cam = O_cam + L * Y_axis_dir
    Z_end_cam = O_cam + L * Z_axis_dir

    # 检查Z坐标是否大于0
    points_cam = [O_cam, X_end_cam, Y_end_cam, Z_end_cam]
    valid_points = []
    for p in points_cam:
        if p[2] > 0:
            valid_points.append(p)
        else:
            print("Point is behind the camera, cannot project.")

    # 投影到图像平面
    projected_points = []
    for p in valid_points:
        X, Y, Z = p
        # 使用内参矩阵K进行投影
        u = (K[0, 0] * X + K[0, 1] * Y + K[0, 2] * Z) / Z
        v = (K[1, 0] * X + K[1, 1] * Y + K[1, 2] * Z) / Z
        projected_points.append((u, v))

    # 转换为图像坐标系（假设图像尺寸为HxW）
    image_points = []
    for u, v in projected_points:
        u_image = int(u)
        v_image = int(v)  # 假设v在相机坐标系中是向上的，图像中是向下的
        image_points.append((u_image, v_image))
    return image_points


def process_segmentation(
    images_path, labels_path, output_base_path, alpha=0.4, plot_pose=True
):
    color_map = {}

    def get_color(class_id):
        if class_id not in color_map:
            np.random.seed(class_id)
            color_map[class_id] = tuple(np.random.randint(0, 256, size=3).tolist())
        return color_map[class_id]

    for img_name in os.listdir(images_path):
        if not img_name.endswith((".jpg", ".png")):
            continue

        label_file = os.path.join(
            labels_path, img_name.replace(".jpg", ".txt").replace(".png", ".txt")
        )
        if not os.path.exists(label_file):
            continue

        pose_file = os.path.join(
            poses_dir, img_name.replace(".jpg", ".txt").replace(".png", ".txt")
        )
        poses = read_poses_from_file(pose_file)
        img_path = os.path.join(images_path, img_name)
        img = cv2.imread(img_path)
        height, width, _ = img.shape
        overlay = img.copy()

        with open(label_file, "r") as f:
            lines = f.readlines()

        class_counts = {}
        for line in lines:
            values = list(map(float, line.split()))
            class_id = int(values[0])
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

        if not class_counts:
            continue

        # 获取出现次数最多的 class_id
        main_class_id = max(class_counts.items(), key=lambda x: x[1])[0]
        output_path = os.path.join(output_base_path, str(main_class_id))
        os.makedirs(output_path, exist_ok=True)

        for line, cur_pose in zip(lines, poses):
            values = list(map(float, line.split()))
            class_id = int(values[0])
            points = np.array(values[1:]).reshape(-1, 2)
            points[:, 0] *= width
            points[:, 1] *= height
            points = points.astype(int)

            fill_color = get_color(class_id)
            contour_color = (255, 255, 255)

            cv2.fillPoly(overlay, [points], fill_color)
            cv2.polylines(
                overlay, [points], isClosed=True, color=contour_color, thickness=2
            )

            M = cv2.moments(points)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = points[0][0], points[0][1]

            # cv2.putText(
            #     overlay, str(class_id), (cx, cy),
            #     fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            #     fontScale=0.8, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA
            # )
            if plot_pose:
                image_points = get_axis(cur_pose)
                cv2.circle(img, image_points[0], 3, (0, 255, 0), -1)

                # 绘制X轴（红色）
                cv2.arrowedLine(
                    img, image_points[0], image_points[1], (0, 0, 255), 2, tipLength=0.1
                )
                # 绘制Y轴（绿色）
                cv2.arrowedLine(
                    img, image_points[0], image_points[2], (0, 255, 0), 2, tipLength=0.1
                )
                # 绘制Z轴（蓝色）
                cv2.arrowedLine(
                    img, image_points[0], image_points[3], (255, 0, 0), 2, tipLength=0.1
                )

        output_img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        save_path = os.path.join(output_path, img_name)
        cv2.imwrite(save_path, output_img)


# 判断是否存在 train/val 子目录
if "train" in os.listdir(images_dir) or "val" in os.listdir(images_dir):
    if "train" in os.listdir(images_dir):
        process_segmentation(
            os.path.join(images_dir, "train"),
            os.path.join(labels_dir, "train"),
            os.path.join(output_dir, "train"),
        )
    if "val" in os.listdir(images_dir):
        process_segmentation(
            os.path.join(images_dir, "val"),
            os.path.join(labels_dir, "val"),
            os.path.join(output_dir, "val"),
        )
else:
    process_segmentation(images_dir, labels_dir, output_dir)

print("完成！图像已按主类别保存到对应子目录。")
