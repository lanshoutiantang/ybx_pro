import os
import argparse
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--src_labels',  help="directory to input", default="")
parser.add_argument('--dst_labels', help="directory to output", default="")
parser.add_argument('--resolution_mode', help="resolution mode", default="")
args = parser.parse_args()

src_label_dir = args.src_labels       # 原始 YOLOv8 seg 标签文件夹
dst_label_dir = args.dst_labels       # 处理后保存的文件夹
os.makedirs(dst_label_dir, exist_ok=True) 
resolution_mode = args.resolution_mode 
print(f"Using resolution mode {resolution_mode}")
W_ORI, H_ORI = 1920, 1536
# mode 0: resize + y-crop
W_RESIZE, H_RESIZE = 960, 768
CROP_Y_TOP, CROP_Y_BOTTOM = 144, 48
W_NEW_0 = 960
H_NEW_0 = 576

# mode 1: original center crop
W_NEW_1 = 960
H_NEW_1 = 576
X_START_1 = (W_ORI - W_NEW_1) // 2   # 480
Y_START_1 = (H_ORI - H_NEW_1) // 2   # 480


# =========================
# mode 0: resize -> y crop
# =========================
def process_resize_ycrop(coords):
    """
    coords: [x1,y1,x2,y2,...] normalized in original image (1920×1536)
    return: xs, ys in new image (960×576)
    """
    xs = coords[0::2] * W_ORI
    ys = coords[1::2] * H_ORI

    # resize
    xs *= W_RESIZE / W_ORI
    ys *= H_RESIZE / H_ORI

    # y crop
    ys -= CROP_Y_TOP

    return xs, ys, W_NEW_0, H_NEW_0


# =========================
# mode 1: original center crop
# =========================
def process_center_crop(coords):
    """
    coords: [x1,y1,x2,y2,...] normalized in original image (1920×1536)
    return: xs, ys in new image (960×576)
    """
    xs = coords[0::2] * W_ORI
    ys = coords[1::2] * H_ORI

    xs -= X_START_1
    ys -= Y_START_1

    return xs, ys, W_NEW_1, H_NEW_1


# =========================
# 主处理函数
# =========================
def process_label_file(src_path, dst_path, resolution_mode):
    lines_out = []

    with open(src_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 3:
            continue

        cls_id = parts[0]
        coords = np.array(list(map(float, parts[1:])), dtype=np.float32)
        if len(coords) % 2 != 0:
            continue

        # -------- pipeline dispatch --------
        if int(resolution_mode) == 0:
            xs, ys, W_NEW, H_NEW = process_resize_ycrop(coords)
        elif int(resolution_mode) == 1:
            xs, ys, W_NEW, H_NEW = process_center_crop(coords)
        else:
            raise ValueError(f"Unknown resolution_mode: {resolution_mode}")

        # -------- inside check --------
        inside_x = (xs >= 0) & (xs <= W_NEW)
        inside_y = (ys >= 0) & (ys <= H_NEW)
        inside = inside_x & inside_y
        if not np.any(inside):
            continue

        # -------- clip --------
        xs = np.clip(xs, 0, W_NEW)
        ys = np.clip(ys, 0, H_NEW)

        # -------- normalize --------
        xs_norm = xs / W_NEW
        ys_norm = ys / H_NEW

        coords_out = []
        for x, y in zip(xs_norm, ys_norm):
            coords_out.append(f"{x:.6f}")
            coords_out.append(f"{y:.6f}")

        line_out = " ".join([cls_id] + coords_out)
        lines_out.append(line_out + "\n")

    with open(dst_path, "w") as f:
        f.writelines(lines_out)


# -------- 批量处理 --------
label_files = [f for f in os.listdir(src_label_dir) if f.endswith(".txt")]

for fname in tqdm(label_files, desc="Processing labels"):
    src_path = os.path.join(src_label_dir, fname)
    dst_path = os.path.join(dst_label_dir, fname)
    process_label_file(src_path, dst_path, resolution_mode)

print(f"✅ 标签处理完成！新标签已保存到: {dst_label_dir}")
