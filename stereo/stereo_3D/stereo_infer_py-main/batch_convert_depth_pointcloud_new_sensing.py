import cv2
import numpy as np
import os
import glob
import argparse
import infer_new_sensing
from tqdm import tqdm


# --- 点云保存函数 (无改动) ---
def save_point_cloud(filename, depth_map_mm, color_image, intrinsics, max_z_m=10.0):
    """
    将深度图和彩色图转换为PLY格式的点云并保存。
    """
    # 检查输入是否有效
    if depth_map_mm is None or color_image is None:
        tqdm.write(
            f"  [点云] 警告: 输入深度图或彩色图为空，无法生成 '{os.path.basename(filename)}'。"
        )
        return
    # 检查通道数
    if len(depth_map_mm.shape) != 2:
        tqdm.write(
            f"  [点云] 警告: 深度图不是单通道图像 ({depth_map_mm.shape})，无法生成 '{os.path.basename(filename)}'。"
        )
        return
    if len(color_image.shape) != 3 or color_image.shape[2] != 3:
        tqdm.write(
            f"  [点云] 警告: 彩色图不是3通道图像 ({color_image.shape})，无法生成 '{os.path.basename(filename)}'。"
        )
        return

    # 确保尺寸一致，以彩色图为准
    if depth_map_mm.shape[:2] != color_image.shape[:2]:
        try:
            depth_map_mm = cv2.resize(
                depth_map_mm,
                (color_image.shape[1], color_image.shape[0]),
                interpolation=cv2.INTER_NEAREST,
            )
        except Exception as e:
            tqdm.write(
                f"  [点云] 警告: 调整深度图尺寸失败: {e}，无法生成 '{os.path.basename(filename)}'。"
            )
            return

    fx, fy, cx, cy = (
        intrinsics["fx"],
        intrinsics["fy"],
        intrinsics["cx"],
        intrinsics["cy"],
    )
    points, colors = [], []

    # 使用 NumPy 向量化操作提高效率
    rows, cols = depth_map_mm.shape
    c_grid, r_grid = np.meshgrid(np.arange(cols), np.arange(rows))

    valid_mask = depth_map_mm > 0
    depth_m = depth_map_mm[valid_mask] / 1000.0

    valid_mask_within_range = depth_m <= max_z_m
    if not np.any(valid_mask_within_range):
        tqdm.write(
            f"  [点云] 警告: 没有在 {max_z_m}m 范围内的有效点，无法生成 '{os.path.basename(filename)}'。"
        )
        return

    depth_m = depth_m[valid_mask_within_range]
    r_valid = r_grid[valid_mask][valid_mask_within_range]
    c_valid = c_grid[valid_mask][valid_mask_within_range]

    x_m = (c_valid - cx) * depth_m / fx
    y_m = (r_valid - cy) * depth_m / fy
    z_m = depth_m

    # 检查颜色图像的有效索引
    valid_indices = (r_valid < color_image.shape[0]) & (c_valid < color_image.shape[1])
    if not np.any(valid_indices):
        tqdm.write(
            f"  [点云] 警告: 没有有效的颜色索引，无法生成 '{os.path.basename(filename)}'。"
        )
        return

    # 仅使用有效的索引来提取颜色和坐标
    x_m = x_m[valid_indices]
    y_m = y_m[valid_indices]
    z_m = z_m[valid_indices]
    r_valid = r_valid[valid_indices]
    c_valid = c_valid[valid_indices]

    bgr_colors = color_image[r_valid, c_valid]
    rgb_colors = bgr_colors[:, ::-1]  # BGR to RGB

    points = np.vstack((x_m, y_m, z_m)).T
    colors = rgb_colors.astype(np.uint8)

    if not points.size > 0:
        tqdm.write(
            f"  [点云] 警告: 最终没有有效的点可用于生成 '{os.path.basename(filename)}'。"
        )
        return

    header = f"""ply
format ascii 1.0
element vertex {len(points)}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""
    try:
        with open(filename, "w") as f:
            f.write(header)
            combined_data = np.hstack((points, colors))
            fmt_string = ["%f"] * 3 + ["%d"] * 3
            np.savetxt(f, combined_data, fmt=fmt_string)
    except Exception as e:
        tqdm.write(
            f"  [点云] 警告: 保存PLY文件 '{os.path.basename(filename)}' 失败: {e}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="将文件夹下的RGB和处理后的Depth图像对转换为点云。"
    )
    parser.add_argument(
        "--root_dir",
        type=str,
        default=".",
        help="包含 'output_*' 系列文件夹的根目录路径。默认为当前目录。",
    )
    parser.add_argument("--stereo_param_path", help="camera params file", default=None)
    parser.add_argument(
        "--file_extension",
        type=str,
        default="png",
        help="图像文件扩展名 (例如: png, jpg)。默认为 png。",
    )
    parser.add_argument(
        "--max_depth_m",
        type=float,
        default=5.0,
        help="点云中点的最大有效Z坐标（单位：米）。默认为 5.0。",
    )
    parser.add_argument(
        "--resolution_mode",
        type=int,
        default=0,
        help="0: resize to 960x576, 1: center crop to 960x576",
    )

    parser.add_argument(
        "--clear_edges",
        action="store_true",
        help="启用此项可将深度图最左和最右各48列置为0。",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="处理帧的间隔。例如, 5 表示每 5 帧处理一帧。 1 或 <=0 表示处理所有帧。默认为 1。",
    )

    args = parser.parse_args()
    resolution_mode = args.resolution_mode
    print(f"root_dir: {args.root_dir}")
    print(f"stereo_param_path: {args.stereo_param_path}")
    print(f"resolution_mode: {resolution_mode}")
    print(f"max_depth_m: {args.max_depth_m}m")

    # # --- 查找 output_* 文件夹 ---
    # search_pattern = os.path.join(args.root_dir, "*")  # 确保只查找 output_ 开头的
    # output_dirs = sorted([d for d in glob.glob(search_pattern) if os.path.isdir(d)])

    output_dirs = [args.root_dir]
    print(output_dirs)

    if not output_dirs:
        print(f"在 '{args.root_dir}' 目录下没有找到任何以 '*' 开头的文件夹。")
        return

    print(f"找到 {len(output_dirs)} 个 'output_' 文件夹。开始处理...")

    maps, intrinsics = infer_new_sensing.get_stereo_params(
        args.stereo_param_path, resolution_mode
    )

    # --- 遍历每个 output_* 文件夹 ---
    overall_progress = tqdm(output_dirs, desc="总进度")
    for output_dir_path in overall_progress:
        sample_name = os.path.basename(output_dir_path)
        overall_progress.set_description(f"处理中 {sample_name}")

        # --- 构建所需子文件夹路径 ---
        rgb_dir = os.path.join(output_dir_path, "rgb")
        depth_dir = os.path.join(output_dir_path, "depth")
        pc_output_dir = os.path.join(
            output_dir_path, "pointcloud"
        )  # 输出到同级 pointcloud 文件夹

        if not os.path.isdir(rgb_dir) or not os.path.isdir(depth_dir):
            tqdm.write(
                f"警告: 在 {sample_name} 中未同时找到 'rgb' 和 'depth' 子文件夹，跳过。"
            )
            continue

        os.makedirs(pc_output_dir, exist_ok=True)

        search_path_depth = os.path.join(depth_dir, f"*.{args.file_extension}")
        depth_files = sorted(glob.glob(search_path_depth))

        if not depth_files:
            tqdm.write(
                f"警告: 在 {sample_name}/depth 中未找到 *.{args.file_extension} 文件，跳过。"
            )
            continue

        # --- 应用帧间隔逻辑 ---
        interval = args.interval
        if interval <= 1:
            # 1 或 -1 (或 0) 表示处理所有帧
            sampled_depth_files = depth_files
        else:
            # 每 N 帧采样一次
            sampled_depth_files = depth_files[::interval]
            tqdm.write(
                f"  └─ INFO: 启用帧间隔 {interval}。将处理 {len(sampled_depth_files)} / {len(depth_files)} 帧。"
            )

        # [MODIFIED] 遍历采样后的文件列表
        inner_progress = tqdm(
            sampled_depth_files, desc=f"-> {sample_name}", leave=False
        )
        for depth_path in inner_progress:
            base_filename = os.path.basename(depth_path)
            rgb_path = os.path.join(rgb_dir, base_filename)

            if not os.path.exists(rgb_path):
                tqdm.write(
                    f"  └─ 警告: 找不到对应的RGB文件 '{rgb_path}'，跳过 '{base_filename}'。"
                )
                continue

            depth_image = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
            rgb_image = cv2.imread(rgb_path)

            if depth_image is None or rgb_image is None:
                tqdm.write(
                    f"  └─ 警告: 无法读取 '{depth_path}' 或 '{rgb_path}'，跳过。"
                )
                continue

            # --- [MODIFIED] 在此处对深度图进行边缘清零处理 ---
            if args.clear_edges:
                if (
                    len(depth_image.shape) == 2 and depth_image.shape[1] > 96
                ):  # 确保是单通道且宽度足够
                    depth_image[:, :48] = 0  # 最左侧48列置为0
                    depth_image[:, -48:] = 0  # 最右侧48列置为0
                else:
                    tqdm.write(
                        f"  └─ 警告: 深度图 '{base_filename}' 不是单通道或宽度不足96，无法执行边缘清零。"
                    )

            # 构建输出点云文件路径
            base_name_no_ext = os.path.splitext(base_filename)[0]
            pc_output_path = os.path.join(pc_output_dir, f"{base_name_no_ext}.ply")

            # 保存点云
            save_point_cloud(
                pc_output_path, depth_image, rgb_image, intrinsics, args.max_depth_m
            )

    print(f"\n处理完成！")
    print(f"生成的点云文件已保存在各自 'output_*/pointcloud' 子目录中。")


if __name__ == "__main__":
    main()
