import torch
import converter
from core_rt_small.rt_igev_stereo_inf import IGEVStereo
import cv2
import numpy as np
import argparse
from tqdm import tqdm
import os
from pathlib import Path
import params_reader

DEVICE = "cuda"


class CustomError(Exception):
    pass


def read_stereo_params(stereo_params_path):
    print(f"read cfg file: {stereo_params_path}")
    fs = cv2.FileStorage(stereo_params_path, cv2.FILE_STORAGE_READ)

    if not fs.isOpened():
        raise ValueError(f"无法打开文件: {stereo_params_path}")

    # 读取 P1 矩阵 (3x4)
    p1 = fs.getNode("P1").mat()

    t = fs.getNode("T").mat()

    # 确保 P1 是 3x4 的矩阵
    if p1 is None or p1.shape != (3, 4):
        raise ValueError("P1 矩阵格式错误，应为 3x4")

    # 提取前 3 列作为内参矩阵 (3x3)
    K_stereo = p1[:, :3]
    baseline = np.abs(t[0][0]) / 1000.0

    fs.release()
    return K_stereo, baseline


def processing(image):
    image = image.astype(np.float32)
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)
    image_tensor = torch.tensor(image)

    return image_tensor


def colorize_disparity(disparity_map, colormap=cv2.COLORMAP_JET):
    a = disparity_map
    colored_disparity_map = cv2.applyColorMap(
        cv2.convertScaleAbs(a, alpha=2.0), colormap
    )

    return colored_disparity_map


def disparity_to_depth(disparity, focal_length, baseline):
    disparity[disparity == 0] = 1e-6
    depth = (focal_length * baseline) / (disparity)
    depth = depth * 1000

    return depth


def edge_filter_depth(disp_est, kernel_size=2):
    depth_image_normalized = cv2.normalize(disp_est, None, 0, 255, cv2.NORM_MINMAX)
    depth_image_8bit = np.uint8(depth_image_normalized)
    edges = cv2.Canny(depth_image_8bit, 20, 50)
    kernel_ = np.ones((kernel_size, kernel_size), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel_, iterations=1)

    return edges_dilated


def get_file_name(img_path):
    img_name = img_path.split("/")[-1]

    return img_name


def get_rectification_parameters(stereo_param_path):
    """
    (新) 一次性加载标定文件, 计算 Rectify Maps 和推理所需的内参。
    """
    params = params_reader.read_all_stereo_params(stereo_param_path)
    K1, D1 = params["K1"], params["D1"]
    K2, D2 = params["K2"], params["D2"]
    R, T = params["R"], params["T"]

    image_size = params["image_size"]
    image_size = (int(image_size[0]), int(image_size[1]))  # (width, height)

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

    fx = fx_orig
    fy = fy_orig
    cx = cx_orig - 160
    cy = cy_orig - 144

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
    }

    return maps, intrinsics


def doinference(model, left_path, right_path, save_path, maps, intrinsics):
    map_lx, map_ly, map_rx, map_ry = maps
    fx = intrinsics["fx"]
    baseline = intrinsics["baseline"]
    INF_SIZE = intrinsics["INF_SIZE"]

    dilate_ks = 2
    focal_length = fx

    save_name = get_file_name(left_path)

    left_img_raw = cv2.imread(left_path)
    right_img_raw = cv2.imread(right_path)
    undistorted_left = cv2.remap(
        left_img_raw, map_lx, map_ly, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
    )
    undistorted_right = cv2.remap(
        right_img_raw, map_rx, map_ry, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT
    )
    left = undistorted_left[144:, 160 : (1280 - 160)]
    right = undistorted_right[144:, 160 : (1280 - 160)]

    l = processing(left).to(DEVICE)
    r = processing(right).to(DEVICE)

    output = model(l, r, iters=6, test_mode=True)

    if DEVICE == "cuda":
        output = output.cpu().detach().numpy().squeeze()
    else:
        output = output.detach().numpy().squeeze()

    disp_est = output.astype(np.float32)

    mask = edge_filter_depth(disp_est, dilate_ks)

    edges_masked = mask == 0
    filtered_disp_image = np.where(edges_masked, disp_est, np.inf)

    depth_img = disparity_to_depth(filtered_disp_image, focal_length, baseline)

    depth_img = np.nan_to_num(depth_img, nan=0.0, posinf=0.0, neginf=0.0)

    save_depth = os.path.join(save_path, "depth", save_name)
    save_rgb = os.path.join(save_path, "rgb", save_name)
    # save_disp_color = os.path.join(save_path, "disp_color", save_name)

    os.makedirs(os.path.join(save_path, "depth"), exist_ok=True)
    os.makedirs(os.path.join(save_path, "rgb"), exist_ok=True)
    # os.makedirs(os.path.join(save_path, "disp_color"), exist_ok=True)

    cv2.imwrite(save_depth, depth_img.astype(np.uint16))
    cv2.imwrite(save_rgb, left)
    # cv2.imwrite(save_disp_color, colorize_disparity(disp_est))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--left_directory", help="directory to input", default="left input"
    )
    parser.add_argument(
        "--right_directory", help="directory to input", default="right input"
    )
    parser.add_argument(
        "--output_directory", help="directory to save output", default="output_carpet"
    )
    parser.add_argument("--stereo_param_path", help="camera params file", default=None)
    parser.add_argument(
        "--checkpoint",
        help="用于[推理]的模型权重文件 (.pth)",
        default="checkpoint/igevrt8_s0.1.5.pth",
    )

    # Architecure choices
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
        help="Choose precision type: float16 or bfloat16 or float32",
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

    args = parser.parse_args()

    model = IGEVStereo(args)

    if not os.path.exists(args.checkpoint):
        print(f"[致命错误] 找不到模型权重文件: {args.checkpoint}")
        return
    print(f"加载模型权重文件: {args.checkpoint}")

    checkpoint = torch.load(args.checkpoint, map_location=lambda storage, loc: storage)
    new_state_dict = {k.replace("module.", ""): v for k, v in checkpoint.items()}
    model.load_state_dict(new_state_dict, strict=True)
    model.to(DEVICE)
    model.eval()

    OUT_PATH = args.output_directory
    stereo_param_path = args.stereo_param_path
    if stereo_param_path.endswith(".json"):
        # replace last .json with .yml
        stereo_param_path_yml = stereo_param_path[:-5] + ".yml"
        if not os.path.exists(stereo_param_path_yml):
            json_path = Path(stereo_param_path)
            yml_path = Path(stereo_param_path_yml)
            converter.convert_json_to_stereo_yml(json_path, yml_path)
        stereo_param_path = stereo_param_path_yml

    maps, intrinsics = get_rectification_parameters(stereo_param_path)

    left_dir = args.left_directory
    right_dir = args.right_directory

    left_imgs = sorted([f for f in os.listdir(left_dir) if f.endswith(".png")])
    right_imgs = sorted([f for f in os.listdir(right_dir) if f.endswith(".png")])

    if len(left_imgs) != len(right_imgs):
        raise CustomError("left/right image count mismatch!")

    for l_name, r_name in tqdm(zip(left_imgs, right_imgs), total=len(left_imgs)):
        left_path = os.path.join(left_dir, l_name)
        right_path = os.path.join(right_dir, r_name)
        doinference(model, left_path, right_path, OUT_PATH, maps, intrinsics)
    print("FINISHED INFERENCE!")


if __name__ == "__main__":
    main()
