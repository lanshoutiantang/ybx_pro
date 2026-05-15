import os

import cv2

from check_depth_utils import (
    check_detph,
    check_depth_pr,
    load_yolo_to_mask,
    guess_translation,
    load_pose,
    depth_to_pointcloud,
    toOpen3dCloud,
)
from datetime import datetime
import numpy as np
import pandas as pd
import shutil
import time

# import open3d as o3d
import argparse
from tqdm import tqdm
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


def mv_imgs(imgs_path, dst_path, img_list, stem=".png"):
    os.makedirs(dst_path, exist_ok=True)
    for img_name in img_list:
        img_path = os.path.join(imgs_path, img_name + stem)
        if not os.path.exists(img_path):
            continue
        dst_img_path = os.path.join(dst_path, img_name + stem)
        shutil.move(img_path, dst_img_path)


def load_txt(txt_path, split_class=False):
    lines = []
    with open(txt_path, "r") as f:
        for line in f:
            if not line or line.startswith("#"):  # 跳过空行和注释
                continue
            line = line.strip().split()
            lines.append(line)
    return lines


def is_absolute_path(path: str) -> bool:
    if not path:
        return False
    return os.path.isabs(path)


def use_abs_path_or_join_path(root_path, data_path):
    if is_absolute_path(data_path):
        return data_path
    return os.path.join(root_path, data_path)


def mask_ignore(overlay, label_line, texture=None):
    h, w = overlay.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    coords = [float(x) for x in label_line[1:]]
    points = np.array(
        [
            [int(coords[i] * w), int(coords[i + 1] * h)]
            for i in range(0, len(coords), 2)
        ],
        dtype=np.int32,
    )
    cv2.fillPoly(mask, [points], 255)

    # 获取掩膜区域 bounding box
    x, y, bw, bh = cv2.boundingRect(points)

    # 限制边界，避免越界
    x_end = min(x + bw, w)
    y_end = min(y + bh, h)
    bw = x_end - x
    bh = y_end - y

    # resize 贴图到掩膜大小（限制后尺寸）
    texture_resized = cv2.resize(texture, (bw, bh), interpolation=cv2.INTER_LINEAR)

    # 生成与原图大小一致的背景图
    patch = np.zeros_like(overlay)
    patch[y : y + bh, x : x + bw] = texture_resized

    # 最终贴图 = mask 区域使用纹理，其他用原图
    mask_3c = cv2.merge([mask, mask, mask])
    overlay = np.where(mask_3c == 255, patch, overlay)
    return overlay


def print_to_file(text: str, file_path: str = "result.txt"):
    """
    将字符串追加写入文件末尾，行首添加时间戳

    :param text: 要写入的字符串
    :param file_path: 文件路径
    """
    time_fmt = "%Y-%m-%d %H:%M:%S"
    timestamp = datetime.now().strftime(time_fmt)
    line = f"[{timestamp}] {text}\n"

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line)
    print(text)


def process_one_item(
    depth_pred_item,
    depth_pred_path,
    depth_gt_path,
    labels_path,
    occlusion_path,
    img_path,
    poses_path,
    labels_path_f,
    abs_thresh,
    p_thresh,
    K,
    img_path_f,
    depth_path_f,
    texture_img,
    mask_flag,
    depth_acc_dir,
    resolution_mode,
):
    depth_pred_item_path = os.path.join(depth_pred_path, depth_pred_item)
    depth_gt_item_path = os.path.join(depth_gt_path, depth_pred_item)
    label_path = os.path.join(labels_path, depth_pred_item.replace(".png", ".txt"))
    occ_path = os.path.join(occlusion_path, depth_pred_item.replace(".png", ".txt"))

    pose_item_path = os.path.join(poses_path, depth_pred_item.replace(".png", ".txt"))
    # poses_sample = load_pose(pose_item_path)
    bad_cases_name = []
    total_case = 0
    if not os.path.exists(depth_gt_item_path) or not os.path.exists(label_path):
        return 0, []

    depth_pred = cv2.imread(depth_pred_item_path, cv2.IMREAD_UNCHANGED) / 1000.0
    depth_gt = cv2.imread(depth_gt_item_path, cv2.IMREAD_UNCHANGED) / 1000.0
    if depth_gt.shape[0] == 720:
        depth_gt = depth_gt[144:, 160 : (1280 - 160)]

    elif depth_gt.shape[0] == 1536:
        # # use ROI
        if int(resolution_mode) == 1:
            h, w = 1536, 1920
            inf_h, inf_w = 576, 960
            x_start = (w - inf_w) // 2
            y_start = (h - inf_h) // 2
            depth_gt = depth_gt[y_start : y_start + inf_h, x_start : x_start + inf_w]
        elif int(resolution_mode) == 0:
            depth_gt = cv2.resize(depth_gt, (960, 768), interpolation=cv2.INTER_AREA)
            depth_gt = depth_gt[144 : (768 - 48), :]
        else:
            raise NotImplementedError

    img = cv2.imread(os.path.join(img_path, depth_pred_item))
    overlay = img.copy()
    h, w = depth_pred.shape
    masks = load_yolo_to_mask(label_path, w, h)
    labels_lines = load_txt(label_path)
    occ_lines = load_txt(occ_path)
    total_case += len(masks)
    depth_accs = []
    cur_occ_cnt = 0
    for i, mask in enumerate(masks):
        is_bad = False
        error = check_depth_pr(depth_gt, depth_pred, mask)
        if float(occ_lines[i][1]) >= 0.3 or error.get("abs_recall") is None:
            cur_occ_cnt += int(float(occ_lines[i][1]) >= 0.3)
            depth_accs.append([labels_lines[i][0], *[-1] * 9])
            is_bad = True
        else:
            cur_obj_depth_acc = [
                labels_lines[i][0],
                error["recall"],
                error["precision"],
                error["abs_recall"],
                error["abs_precision"],
                error["abs_rel"],
                error["abs_error"],
                error["err_std"],
                error["p95_err"],
                error["median_abs"],
            ]
            depth_accs.append(cur_obj_depth_acc)

            if abs_thresh is not None:
                if error["abs_error"] >= abs_thresh:
                    is_bad = True
            elif p_thresh is not None:
                if (
                    error["precision"] < p_thresh
                ):  # or error["Coverage"] < coverage_thresh:
                    # if error["MAE"] > abs_thresh or error["Coverage"] < coverage_thresh:
                    is_bad = True

            else:
                raise NotImplementedError
        if is_bad:
            # labels_lines[i][0] = -1
            # print(error)
            bad_cases_name.append(depth_pred_item.split(".")[0] + f"_{i}")
            if mask_flag:
                overlay = mask_ignore(overlay, labels_lines[i], texture=texture_img)

    # If have good case
    # if len(bad_cases_name) < total_case:
    # lines = [" ".join(map(str, lbl)) + "\n" for lbl in labels_lines]
    # with open(os.path.join(labels_path_f, depth_pred_item.replace(".png", ".txt")), "w") as f:
    #     f.writelines(lines)
    # cv2.imwrite(str(img_path_f / depth_pred_item), overlay)
    #     shutil.copy(depth_pred_item_path, str(depth_path_f / depth_pred_item))

    # depth_acc_lines = [" ".join(map(str, lbl)) + "\n" for lbl in depth_accs]
    # depth_acc_lines = [" ".join("{:.4f}".format(x) for x in lbl) + "\n" for lbl in depth_accs]
    depth_acc_lines = [
        " ".join(
            [str(int(val)) if idx == 0 else f"{val:.4f}" for idx, val in enumerate(lbl)]
        )
        + "\n"
        for lbl in depth_accs
    ]
    with open(
        os.path.join(depth_acc_dir, depth_pred_item.replace(".png", ".txt")), "w"
    ) as f:
        f.writelines(depth_acc_lines)

    return total_case, bad_cases_name, cur_occ_cnt


if __name__ == "__main__":
    # data_root = "/home/ubt/ws/data/sanyi/sanyi_val_orin/4/"
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", help="data root dir", default="input")
    parser.add_argument(
        "--stereo_depth", help="directory to input stereo depth", default="depth"
    )
    parser.add_argument("--sim_depth", help="directory", default="depth_sim")
    parser.add_argument("--labels", help="directory", default="labels")
    parser.add_argument("--occlusion", help="directory", default="occlusion")
    parser.add_argument("--images", help="directory", default="images")
    parser.add_argument(
        "--depth_acc", help="depth_acc directory", default="depth_acc_v017"
    )
    parser.add_argument("--poses", help="directory", default="posess")
    parser.add_argument("--badcase_dir", help="directory", default="bad_case960_p")
    parser.add_argument("--abs_thresh", help="threshold", type=float)
    parser.add_argument("--p_thresh", help="threshold", type=float)
    parser.add_argument("--resolution_mode", help="resolution mode", type=int)
    parser.add_argument(
        "--mask_flag", action="store_true", help="mask bad depth case in img or not"
    )

    args = parser.parse_args()
    num_workers = 16
    data_root = args.data_root
    move_bad_cases = False
    abs_thresh = args.abs_thresh
    resolution_mode = args.resolution_mode
    print(f"Using resolution mode {resolution_mode}")
    p_thresh = args.p_thresh
    coverage_thresh = 0.5
    print(f"abs thresh: {abs_thresh}, p thresh: {p_thresh}")
    bad_cases_name = set()

    depth_pred_path = use_abs_path_or_join_path(data_root, args.stereo_depth)
    depth_gt_path = use_abs_path_or_join_path(data_root, args.sim_depth)
    labels_path = use_abs_path_or_join_path(data_root, args.labels)
    occlusion_path = use_abs_path_or_join_path(data_root, args.occlusion)
    img_path = use_abs_path_or_join_path(data_root, args.images)
    poses_path = use_abs_path_or_join_path(data_root, args.poses)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    texture_img = cv2.imread(os.path.join(current_dir, "20250618-192424.jpg"))

    debug_dir = os.path.join(data_root, "ply")
    labels_path_f = Path(data_root) / "labels_960_f"
    if labels_path_f.exists():
        shutil.rmtree(labels_path_f)
    # labels_path_f.mkdir(exist_ok=True, parents=True)
    img_path_f = Path(data_root) / "rgb_960_f"
    if img_path_f.exists():
        shutil.rmtree(img_path_f)
    # img_path_f.mkdir(exist_ok=True, parents=True)
    depth_path_f = Path(data_root) / "stereo_depth_960_f"
    if depth_path_f.exists():
        shutil.rmtree(depth_path_f)
    # depth_path_f.mkdir(exist_ok=True, parents=True)
    depth_acc_dir = Path(data_root) / args.depth_acc
    print(depth_acc_dir)
    depth_acc_dir.mkdir(exist_ok=True, parents=True)

    bad_case_root = os.path.join(data_root, args.badcase_dir)
    os.makedirs(bad_case_root, exist_ok=True)
    # bad case save folder
    # bad_cases_img_path = os.path.join(bad_case_root, "images")
    # bad_cases_depth_path = os.path.join(bad_case_root, "depth")
    # bad_cases_labels_path = os.path.join(bad_case_root, "label")
    # bad_cases_pose_path = os.path.join(bad_case_root, "pose")
    # os.makedirs(debug_dir, exist_ok=True)

    # if move_bad_cases:
    #     os.makedirs(bad_cases_img_path, exist_ok=True)

    # fx = 281.66891056887016
    # fy = 281.66891056887016
    # cx = 304.0
    # cy = 150.0
    fx = 433.33678549056947
    fy = 433.33678549056947
    cx = 480.0
    cy = 216.0
    # fx = 278.930973893
    # fy = 278.930973893
    # cx = 304.0
    # cy = 192.0
    fx = 388.6014963549259
    fy = 388.6014963549259
    cx = 480.0
    cy = 240.0

    # # use ROI
    # fx = 777.20299270985186
    # fy = 777.20299270985186
    # cx = 480.0
    # cy = 288.0

    k_vector = np.array([fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0])
    K = k_vector.reshape(3, 3)
    total_occ_cnt = 0
    depth_pred = os.listdir(depth_pred_path)
    depth_gt = os.listdir(depth_gt_path)
    # imgs = os.listdir(img_path)

    if len(depth_pred) != len(depth_gt):
        print("depth prediction and ground truth are not equal")

    func = partial(
        process_one_item,
        depth_pred_path=depth_pred_path,
        depth_gt_path=depth_gt_path,
        labels_path=labels_path,
        occlusion_path=occlusion_path,
        img_path=img_path,
        poses_path=poses_path,
        labels_path_f=labels_path_f,
        abs_thresh=abs_thresh,
        p_thresh=p_thresh,
        K=K,
        img_path_f=img_path_f,
        depth_path_f=depth_path_f,
        texture_img=texture_img,
        mask_flag=args.mask_flag,
        depth_acc_dir=depth_acc_dir,
        resolution_mode=resolution_mode,
    )
    all_bad_names = []
    total_case_sum = 0
    bad_case_sum = 0
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(func, depth_pred), total=len(depth_pred)))

    # ---------- 汇总统计 ----------
    for total_num, bad_names, occ_cnt in results:
        bad_case_sum += len(bad_names) - occ_cnt
        total_case_sum += total_num
        total_occ_cnt += occ_cnt
        all_bad_names.extend(bad_names)
    bad_case_sum -= total_occ_cnt

    print_to_file(f"bad case objects number: {bad_case_sum}")
    print_to_file(f"total case objects number: {total_case_sum}")
    print_to_file(f"{data_root} stereo depth ratio: {bad_case_sum / total_case_sum}")
    print_to_file(f"{data_root} stereo depth occlusion count: {total_occ_cnt}")
    pd_frame = pd.DataFrame(list(all_bad_names), index=None)
    pd_frame.to_csv(os.path.join(bad_case_root, f"bad_cases_{abs_thresh}.csv"))

    # print(bad_cases_name)
    # if move_bad_cases:
    #     mv_imgs(img_path, bad_cases_img_path, bad_cases_name, stem='.png')
    # mv_imgs(depth_pred_path, bad_cases_depth_path, bad_cases_name, stem='.png')
    # mv_imgs(labels_path, bad_cases_labels_path, bad_cases_name, stem='.txt')
    # mv_imgs(poses_path, bad_cases_pose_path, bad_cases_name, stem='.txt')
