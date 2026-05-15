import math
import torch
import converter
from core_rt_small.rt_igev_stereo_inf import IGEVStereo
import cv2
import numpy as np
import argparse
from tqdm import tqdm
import os
from pathlib import Path
import re
import files_op_py
import params_reader
import torch.multiprocessing as mp

# ==================================================================
# == 部分 1: 推理所需的辅助函数  ==
# ==================================================================

DEVICE = "cuda"


class CustomError(Exception):
    pass


def processing(image):
    """(Script 1) 将图像 NumPy 数组转换为 Tensor"""
    image = image.astype(np.float32)
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)
    image_tensor = torch.tensor(image)
    return image_tensor


def colorize_disparity(disparity_map, colormap=cv2.COLORMAP_JET):
    """(Script 1) 视差图上色"""
    a = disparity_map
    colored_disparity_map = cv2.applyColorMap(
        cv2.convertScaleAbs(a, alpha=2.0), colormap
    )
    return colored_disparity_map


def disparity_to_depth(disparity, focal_length, baseline):
    """(Script 1) 视差转深度"""
    disparity[disparity == 0] = 1e-6
    depth = (focal_length * baseline) / (disparity)
    depth = depth * 1000
    return depth


def edge_filter_depth(disp_est, kernel_size=2):
    """(Script 1) 深度图边缘过滤"""
    depth_image_normalized = cv2.normalize(disp_est, None, 0, 255, cv2.NORM_MINMAX)
    depth_image_8bit = np.uint8(depth_image_normalized)
    edges = cv2.Canny(depth_image_8bit, 20, 50)
    kernel_ = np.ones((kernel_size, kernel_size), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel_, iterations=1)
    return edges_dilated


# ==================================================================
# == 部分 2: 图像匹配所需的辅助函数 (来自 Script 2) ==
# ==================================================================


def extract_index_and_ts(filename):
    """
    (已更新) 自适应匹配两种文件名格式：
    1. "index_timestamp.png" (例如: 123_456.789.png)
    2. "timestamp.png" (例如: 456.789.png)
    """

    # 模式1: 优先匹配 "index_timestamp.png"
    match1 = re.match(r"(\d+)_(\d+\.\d+)\.png", filename)
    if match1:
        return match1.group(1), match1.group(2)  # 返回 (index, timestamp)

    # 模式2: 匹配 "timestamp.png"
    match2 = re.match(r"(\d+\.\d+)\.png", filename)
    if match2:
        ts = match2.group(1)
        return ts, ts  # 返回 (timestamp, timestamp) 作为 (idx, ts)

    # 两种模式都不匹配
    return None, None


# ==================================================================
# == 部分 3: 融合后的核心功能 (新) ==
# ==================================================================


def get_stereo_params(stereo_param_path, resolution_mode=0):
    params = params_reader.read_all_stereo_params(stereo_param_path)
    if (
        params["K1"] is None
        or params["D1"] is None
        or params["K2"] is None
        or params["D2"] is None
    ):
        print("use get_no_distorted_params()")
        return get_no_distorted_params(stereo_param_path, resolution_mode)
    else:
        print("use get_rectification_params()")
        return get_rectification_params(stereo_param_path, resolution_mode)


def get_no_distorted_params(stereo_param_path, resolution_mode=0):
    params = params_reader.read_all_stereo_params(stereo_param_path)
    T = params["T"]
    K_stereo = params["K_stereo"]
    image_size = params["image_size"]
    baseline = np.abs(T[0][0]) / 1000.0  # 基线 (米)

    fx_orig, fy_orig = K_stereo[0][0], K_stereo[1][1]
    cx_orig, cy_orig = K_stereo[0][2], K_stereo[1][2]

    # (来自 Script 1 的硬编码) 应用推理尺寸的缩放和裁剪调整
    INF_SIZE = [576, 960]  # TODO: refactor later
    inf_h, inf_w = INF_SIZE
    h, w = int(image_size[1].item()), int(image_size[0].item())  # (height, width)

    if resolution_mode == 0:
        fx = fx_orig * 0.5  # 对应 1920 -> 960 的缩放
        fy = fy_orig * 0.5  # 对应 1536 -> 768 的缩放
        cx = cx_orig * 0.5
        cy = cy_orig * 0.5 - 144  # 对应 144:(768 - 48) 的裁剪
    elif resolution_mode == 1:  # center crop
        x_start = (w - inf_w) // 2
        y_start = (h - inf_h) // 2

        fx = fx_orig
        fy = fy_orig
        cx = cx_orig - x_start
        cy = cy_orig - y_start
    elif resolution_mode == 2:  # full resolution
        x_start = w % 32
        y_start = h % 32
        h_cropped = h - y_start
        w_cropped = w - x_start

        INF_SIZE = [h_cropped, w_cropped]
        fx = fx_orig
        fy = fy_orig
        cx = cx_orig - x_start
        cy = cy_orig - y_start
    else:
        raise CustomError(f"未知的 resolution_mode: {resolution_mode}")

    print("已成功计算 Rectification Maps。")
    print(f"推理尺寸 (INF_SIZE): {INF_SIZE}")
    print(f"推理用内参 (已调整): fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}")
    print(f"推理用基线: {baseline:.4f} m")

    maps = (None, None, None, None)
    intrinsics = {
        "fx": fx,
        "fy": fy,
        "cx": cx,
        "cy": cy,
        "baseline": baseline,
        "INF_SIZE": INF_SIZE,
        "resolution_mode": resolution_mode,
    }

    return maps, intrinsics


def get_rectification_params(stereo_param_path, resolution_mode=0):
    """
    (新) 一次性加载标定文件, 计算 Rectify Maps 和推理所需的内参。
    """
    params = params_reader.read_all_stereo_params(stereo_param_path)
    K1, D1 = params["K1"], params["D1"]
    K2, D2 = params["K2"], params["D2"]
    R, T = params["R"], params["T"]
    image_size = params["image_size"]
    h, w = int(image_size[1].item()), int(image_size[0].item())

    image_size = (w, h)  # (width, height)
    alpha = params.get("alpha_stereo_rectify", -1)

    # 1. 计算双目校正参数
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
        K1, D1, K2, D2, image_size, R, T, flags=cv2.CALIB_ZERO_DISPARITY, alpha=alpha
    )

    # 2. 计算 Rectification Maps (供 cv2.remap 使用)
    map_lx, map_ly = cv2.initUndistortRectifyMap(
        K1, D1, R1, P1, image_size, cv2.CV_32FC1
    )
    map_rx, map_ry = cv2.initUndistortRectifyMap(
        K2, D2, R2, P2, image_size, cv2.CV_32FC1
    )

    # 3. 提取并调整推理所需的内参
    K_stereo = P1[:, :3]
    baseline = np.abs(T[0][0]) / 1000.0  # 基线 (米)

    fx_orig, fy_orig = K_stereo[0][0], K_stereo[1][1]
    cx_orig, cy_orig = K_stereo[0][2], K_stereo[1][2]

    # (来自 Script 1 的硬编码) 应用推理尺寸的缩放和裁剪调整
    INF_SIZE = [576, 960]  # TODO: refactor later
    inf_h, inf_w = INF_SIZE

    if resolution_mode == 0:
        fx = fx_orig * 0.5  # 对应 1920 -> 960 的缩放
        fy = fy_orig * 0.5  # 对应 1536 -> 768 的缩放
        cx = cx_orig * 0.5
        cy = cy_orig * 0.5 - 144  # 对应 144:(768 - 48) 的裁剪
    elif resolution_mode == 1:  # center crop
        x_start = (w - inf_w) // 2
        y_start = (h - inf_h) // 2

        fx = fx_orig
        fy = fy_orig
        cx = cx_orig - x_start
        cy = cy_orig - y_start
    elif resolution_mode == 2:  # full resolution
        x_start = w % 32
        y_start = h % 32
        h_cropped = h - y_start
        w_cropped = w - x_start

        INF_SIZE = [h_cropped, w_cropped]
        fx = fx_orig
        fy = fy_orig
        cx = cx_orig - x_start
        cy = cy_orig - y_start
    else:
        raise CustomError(f"未知的 resolution_mode: {resolution_mode}")

    print("已成功计算 Rectification Maps。")
    print(f"推理尺寸 (INF_SIZE): {INF_SIZE}")
    print(f"推理用内参 (已调整): fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}")
    print(f"推理用基线: {baseline:.4f} m")

    maps = (map_lx, map_ly, map_rx, map_ry)
    intrinsics = {
        "fx": fx,
        "fy": fy,
        "cx": cx,
        "cy": cy,
        "baseline": baseline,
        "INF_SIZE": INF_SIZE,
        "resolution_mode": resolution_mode,
    }

    return maps, intrinsics


def do_inference_in_memory(
    model, left_rectified, right_rectified, save_name, save_path, intrinsics
):
    """
    (新) 接收内存中的图像, 执行推理并保存结果。

    Args:
        model: 已加载的 IGEVStereo 模型
        left_rectified (np.array): 内存中的左图 (1920x1536)
        right_rectified (np.array): 内存中的右图 (1920x1536)
        save_name (str): 输出文件名 (e.g., "timestamp.png")
        save_path (str): 输出子目录 (e.g., ".../output/subdir1")
        intrinsics (tuple): (fx, fy, cx, cy, baseline, INF_SIZE)
    """
    fx = intrinsics["fx"]
    baseline = intrinsics["baseline"]
    INF_SIZE = intrinsics["INF_SIZE"]
    inf_h, inf_w = INF_SIZE
    resolution_mode = intrinsics["resolution_mode"]

    # 1. (来自 Script 1 - read_imgs) 缩放和裁剪
    if resolution_mode == 0:
        # 将 1920x1536 的输入图 -> 960x768 -> 裁剪为 576x960
        left_image = cv2.resize(
            left_rectified, (960, 768), interpolation=cv2.INTER_AREA
        )
        right_image = cv2.resize(
            right_rectified, (960, 768), interpolation=cv2.INTER_AREA
        )

        left_image = left_image[144 : (768 - 48), :]  # Crop to 576x960
        right_image = right_image[144 : (768 - 48), :]
    elif resolution_mode == 1:
        # Center crop 1920x1536 的输入图 -> 960x576
        h, w = left_rectified.shape[0:2]
        x_start = (w - inf_w) // 2
        y_start = (h - inf_h) // 2

        left_image = left_rectified[
            y_start : y_start + inf_h, x_start : x_start + inf_w
        ]
        right_image = right_rectified[
            y_start : y_start + inf_h, x_start : x_start + inf_w
        ]
    elif resolution_mode == 2:
        # full resolution
        h, w = left_rectified.shape[0:2]
        x_start = w % 32
        y_start = h % 32

        left_image = left_rectified[
            y_start : y_start + inf_h, x_start : x_start + inf_w
        ]
        right_image = right_rectified[
            y_start : y_start + inf_h, x_start : x_start + inf_w
        ]
    else:
        raise CustomError(f"未知的 resolution_mode: {resolution_mode}")

    # 2. (来自 Script 1 - processing) 转换为 Tensor
    l = processing(left_image).to(DEVICE)
    r = processing(right_image).to(DEVICE)

    # 3. (来自 Script 1 - doinference) 执行模型推理
    output = model(l, r, iters=6, test_mode=True)

    if DEVICE == "cuda":
        output = output.cpu().detach().numpy().squeeze()
    else:
        output = output.detach().numpy().squeeze()

    disp_est = output.astype(np.float32)

    # 4. (来自 Script 1 - doinference) 后处理和深度转换
    mask = edge_filter_depth(disp_est, kernel_size=2)
    edges_masked = mask == 0
    filtered_disp_image = np.where(edges_masked, disp_est, np.inf)

    depth_img = disparity_to_depth(filtered_disp_image, fx, baseline)
    depth_img = np.nan_to_num(depth_img, nan=0.0, posinf=0.0, neginf=0.0)

    # 5. (来自 Script 1 - doinference) 保存结果
    save_depth_path = os.path.join(save_path, "depth", save_name)
    save_rgb_path = os.path.join(save_path, "rgb", save_name)

    os.makedirs(os.path.join(save_path, "depth"), exist_ok=True)
    os.makedirs(os.path.join(save_path, "rgb"), exist_ok=True)

    cv2.imwrite(save_depth_path, depth_img.astype(np.uint16))
    cv2.imwrite(save_rgb_path, left_image)  # 保存裁剪/缩放后的左图


def run_pipeline_in_memory(args, model, maps, intrinsics):
    """
    (新) 遍历所有子目录, 在内存中执行 "Remap -> Infer" 流程。
    """
    map_lx, map_ly, map_rx, map_ry = maps

    # sub_dirs = files_op_py.get_subdirectories(args.root_data_path)
    # if not sub_dirs:
    #     print(f"[错误] 在 {args.root_data_path} 中未找到任何子目录。")
    #     return

    sub_dirs = [args.root_data_path]

    for sub_dir in sorted(sub_dirs):
        sub_dir_name = os.path.basename(sub_dir)
        print(f"\n========== 正在处理: {sub_dir_name} ==========")

        left_data_path = os.path.join(sub_dir, "left")
        right_data_path = os.path.join(sub_dir, "right")

        # 最终输出路径
        if len(sub_dirs) == 1:
            output_save_path = args.output_directory
        else:
            output_save_path = os.path.join(args.output_directory, sub_dir_name)

        if not os.path.isdir(left_data_path) or not os.path.isdir(right_data_path):
            print(f"  [警告] 在 {sub_dir} 中找不到 'left' 或 'right' 目录。跳过。")
            continue

        # (来自 Script 2) 使用时间戳匹配左右图像
        left_files = files_op_py.get_file_paths(left_data_path, "*.png")
        right_files = files_op_py.get_file_paths(right_data_path, "*.png")
        left_files.sort()
        right_files.sort()
        if not left_files or not right_files:
            print(f"  [警告] 在 {sub_dir} 中找不到任何 PNG 图像。跳过。")
            continue

        left_map = {}
        right_map = {}

        for file in left_files:
            name = os.path.basename(file)
            idx, ts = extract_index_and_ts(name)
            if idx and ts:
                left_map[idx] = (file, ts)

        for file in right_files:
            name = os.path.basename(file)
            idx, _ = extract_index_and_ts(name)
            if idx:
                right_map[idx] = file

        if not left_map or not right_map:
            index = 0
            for left_file, right_file in zip(left_files, right_files):
                basename = os.path.basename(left_file)[:-4]  # remove ".png"
                left_map[index] = (left_file, basename)
                right_map[index] = right_file
                index += 1

        if not left_map or not right_map:
            print(f"  [警告] 在 {sub_dir_name} 中没有找到匹配的图像。跳过。")
            continue

        print(f"  找到 {len(left_map)} 对匹配的图像。开始处理...")

        # 遍历所有匹配的图像
        for idx in tqdm(sorted(left_map.keys()), desc=f"  推理 {sub_dir_name}"):
            if idx not in right_map:
                continue  # 理论上不会发生，但作为安全检查

            left_path, timestamp = left_map[idx]
            right_path = right_map[idx]

            # 1. 读取原始图像
            left_img_raw = cv2.imread(left_path)
            right_img_raw = cv2.imread(right_path)

            if left_img_raw is None or right_img_raw is None:
                print(f"\n  [错误] 读取图像失败 {left_path} 或 {right_path}. 跳过。")
                continue

            # 2. 去畸变 (在内存中)
            if map_lx is None or map_ly is None or map_rx is None or map_ry is None:
                undistorted_left = left_img_raw
                undistorted_right = right_img_raw
            else:
                undistorted_left = cv2.remap(
                    left_img_raw, map_lx, map_ly, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
                )
                undistorted_right = cv2.remap(
                    right_img_raw, map_rx, map_ry, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
                )

            # 3. 推理 (在内存中)
            out_name = f"{timestamp}.png"
            do_inference_in_memory(
                model,
                undistorted_left,
                undistorted_right,
                out_name,
                output_save_path,
                intrinsics,
            )


def collect_image_pairs(args):
    """
    收集所有需要处理的 (idx, left_path, right_path, timestamp)
    """
    sub_dirs = [args.root_data_path]
    all_pairs = []

    for sub_dir in sorted(sub_dirs):
        left_data_path = os.path.join(sub_dir, args.left_folder)
        right_data_path = os.path.join(sub_dir, "right")

        if not os.path.isdir(left_data_path) or not os.path.isdir(right_data_path):
            continue

        left_files = sorted(files_op_py.get_file_paths(left_data_path, "*.png"))
        right_files = sorted(files_op_py.get_file_paths(right_data_path, "*.png"))

        if not left_files or not right_files:
            continue

        left_map, right_map = {}, {}

        for file in left_files:
            name = os.path.basename(file)
            idx, ts = extract_index_and_ts(name)
            if idx is not None and ts is not None:
                left_map[idx] = (file, ts)

        for file in right_files:
            name = os.path.basename(file)
            idx, _ = extract_index_and_ts(name)
            if idx is not None:
                right_map[idx] = file

        # fallback：按顺序匹配
        if not left_map or not right_map:
            for i, (lf, rf) in enumerate(zip(left_files, right_files)):
                ts = os.path.basename(lf)[:-4]
                left_map[i] = (lf, ts)
                right_map[i] = rf

        for idx in sorted(left_map.keys()):
            if idx not in right_map:
                continue
            left_path, ts = left_map[idx]
            right_path = right_map[idx]
            all_pairs.append((idx, left_path, right_path, ts))

    return all_pairs


def worker_process_in_memory(
    gpu_id,
    pairs,
    maps,
    intrinsics,
    args,
):
    """
    每个 GPU 一个进程
    """
    # -------------------------------
    #  绑定 GPU
    # -------------------------------
    torch.cuda.set_device(gpu_id)
    device = (
        torch.device(f"cuda:{gpu_id}")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )

    # -------------------------------
    #  加载模型（只一次）
    # -------------------------------
    model = IGEVStereo(args)  # 你自己的模型构建
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    new_state_dict = {k.replace("module.", ""): v for k, v in checkpoint.items()}
    model.load_state_dict(new_state_dict, strict=True)
    model.to(device)
    model.eval()

    map_lx, map_ly, map_rx, map_ry = maps

    progress = (
        tqdm(pairs, desc=f"GPU {gpu_id}", position=gpu_id) if gpu_id == 0 else pairs
    )

    with torch.no_grad():
        for _, left_path, right_path, timestamp in progress:
            # 1. 读图
            left_img = cv2.imread(left_path)
            right_img = cv2.imread(right_path)
            if left_img is None or right_img is None:
                continue

            # 2. remap
            if map_lx is not None:
                left_img = cv2.remap(
                    left_img, map_lx, map_ly, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
                )
                right_img = cv2.remap(
                    right_img, map_rx, map_ry, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
                )

            # 3. inference
            out_name = f"{timestamp}.png"
            do_inference_in_memory(
                model,
                left_img,
                right_img,
                out_name,
                args.output_directory,
                intrinsics,
            )


def split_list(lst, n):
    """把 lst 均匀切成 n 份"""
    k = math.ceil(len(lst) / n)
    return [lst[i : i + k] for i in range(0, len(lst), k)]


def run_pipeline_multi_gpu(args, maps, intrinsics):
    all_pairs = collect_image_pairs(args)

    if len(all_pairs) == 0:
        print("没有可处理的数据")
        return

    num_gpus = args.num_gpus if args.num_gpus > 0 else torch.cuda.device_count()
    print(f"Using {num_gpus} GPUs")
    num_process = max(num_gpus, 1)

    pair_chunks = split_list(all_pairs, num_process)

    mp.set_start_method("spawn", force=True)
    processes = []

    for gpu_id, pairs in enumerate(pair_chunks):
        if len(pairs) == 0:
            continue

        p = mp.Process(
            target=worker_process_in_memory,
            args=(
                gpu_id,
                pairs,
                maps,
                intrinsics,
                args,
            ),
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


# ==================================================================
# == 部分 4: 主函数 (新) ==
# ==================================================================


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="全内存自动化立体视觉流水线 (去畸变 -> 深度推理)"
    )

    # --- 统一的路径参数 ---
    parser.add_argument(
        "--stereo_param_path",
        help="用于[去畸变]的立体相机标定文件 (e.g., stereo_cam.yml)",
        required=True,
    )
    parser.add_argument(
        "--root_data_path",
        help="包含[原始]图像的根目录 (e.g., .../new_sensing_shiyan)",
        required=True,
    )
    parser.add_argument(
        "--output_directory",
        help="保存[最终]深度图和RGB图的根目录 (e.g., .../shiyan_output)",
        required=True,
    )
    parser.add_argument(
        "--checkpoint",
        help="用于[推理]的模型权重文件 (.pth)",
        default="checkpoint/igevrt8_s0.1.5.pth",
    )
    parser.add_argument(
        "--resolution_mode",
        type=int,
        default=0,
        help="0: resize to 960x576, 1: center crop to 960x576, 2: full resolution(h w is multiples of 32)",
    )

    # --- 推理模型架构参数 (来自 Script 1) ---
    parser.add_argument(
        "--mixed_precision",
        default=False,
        action="store_true",
        help="use mixed precision",
    )
    parser.add_argument(
        "--precision_dtype",
        default="float32",
        choices=["float16", "bfloat16", "float32"],
        help="Choose precision type",
    )
    parser.add_argument(
        "--hidden_dim",
        nargs="+",
        type=int,
        default=96,
        help="hidden state and context dimensions",
    )
    parser.add_argument(
        "--corr_levels",
        type=int,
        default=2,
        help="number of levels in the correlation pyramid",
    )
    parser.add_argument(
        "--corr_radius", type=int, default=4, help="width of the correlation pyramid"
    )
    parser.add_argument(
        "--n_downsample",
        type=int,
        default=2,
        help="resolution of the disparity field (1/2^K)",
    )
    parser.add_argument(
        "--n_gru_layers", type=int, default=3, help="number of hidden GRU levels"
    )
    parser.add_argument(
        "--max_disp", type=int, default=192, help="max disp of geometry encoding volume"
    )
    parser.add_argument(
        "--num_gpus",
        type=int,
        default=8,
        help="number of GPUs to use",
    )
    parser.add_argument(
        "--left_folder",
        default="left",
        help="left folder name",
    )

    args = parser.parse_args(argv)

    stereo_param_path = args.stereo_param_path
    if stereo_param_path.endswith(".json"):
        # replace last .json with .yml
        stereo_param_path_yml = stereo_param_path[:-5] + ".yml"
        if not os.path.exists(stereo_param_path_yml):
            json_path = Path(stereo_param_path)
            yml_path = Path(stereo_param_path_yml)
            converter.convert_json_to_stereo_yml(json_path, yml_path)
        stereo_param_path = stereo_param_path_yml

    print(f"root_data_path: {args.root_data_path}")
    print(f"output_directory: {args.output_directory}")
    print(f"stereo_param_path: {args.stereo_param_path}")
    print(f"checkpoint: {args.checkpoint}")
    print(f"resolution_mode: {args.resolution_mode}")

    print(f"使用 OpenCV: {cv2.__version__}")
    print("--- 开始步骤 1: 加载标定文件并计算 Maps ---")

    resolution_mode = args.resolution_mode
    try:
        maps, intrinsics = get_stereo_params(stereo_param_path, resolution_mode)
    except Exception as e:
        print(f"[致命错误] 无法加载或处理标定文件: {e}")
        return

    ## write cam_param to txt file
    os.makedirs(os.path.join(args.output_directory, "depth"), exist_ok=True)
    cam_param_txt_path = os.path.join(args.output_directory, "cam_param.txt")
    with open(cam_param_txt_path, "w") as f:
        f.write(f"fx: {intrinsics['fx']} ")
        f.write(f"fy: {intrinsics['fy']} ")
        f.write(f"cx: {intrinsics['cx']} ")
        f.write(f"cy: {intrinsics['cy']} \n")
        f.write(f"baseline: {intrinsics['baseline']} ")
        f.write(f"INF_SIZE: {intrinsics['INF_SIZE']} ")
        f.write(f"resolution_mode: {intrinsics['resolution_mode']} ")
    print(f"相机参数已写入: {cam_param_txt_path}")

    print("\n--- 开始步骤 2: 加载深度推理模型 ---")

    if not os.path.exists(args.checkpoint):
        print(f"[致命错误] 找不到模型权重文件: {args.checkpoint}")
        return
    print(f"加载模型权重文件: {args.checkpoint}")

    model = IGEVStereo(args)
    checkpoint = torch.load(args.checkpoint, map_location=lambda storage, loc: storage)
    new_state_dict = {k.replace("module.", ""): v for k, v in checkpoint.items()}
    model.load_state_dict(new_state_dict, strict=True)
    model.to(DEVICE)
    model.eval()
    print("模型加载成功。")

    print("\n--- 开始步骤 3: 运行全内存处理流水线 ---")
    # run_pipeline_multi_gpu(args, maps, intrinsics)
    run_pipeline_in_memory(args, model, maps, intrinsics)

    print("\n--- 所有流水线步骤已完成! ---")


def main_debug():
    main(
        [
            "--root_data_path",
            "/media/ubt/data/head/20251216_fenjian/sanyi_1023_val",
            "--output_directory",
            "/media/ubt/data/head/20251216_fenjian/results",
            "--stereo_param_path",
            "/media/ubt/data/head/20251216_fenjian/stereo_cam_1920.yml",
            "--checkpoint",
            "./checkpoint/igevrt8_s0.1.5.pth",
            "--resolution_mode",
            "1",
        ]
    )


if __name__ == "__main__":
    main()

    # main_debug()
