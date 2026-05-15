import cv2
import numpy as np
import pickle
import os
# import open3d as o3d
# from shapely.geometry import Polygon
# from extract_mask_pose import load_yolo_polygon, compute_iou


# def load_yolo_polygon(txt_path, img_w, img_h):
#     """读取yolov8 txt segmentation，返回list[Polygon]"""
#     polys = []
#     with open(txt_path, "r") as f:
#         for line in f.readlines():
#             parts = line.strip().split()
#             if len(parts) < 3:
#                 continue
#             coords = list(map(float, parts[1:]))
#             pts = [(coords[i] * img_w, coords[i+1] * img_h) for i in range(0, len(coords), 2)]
#             poly = Polygon(pts)
#             if not poly.is_valid or poly.area < 1:
#                 continue
#             polys.append(poly)
#     return polys

def compute_iou(poly1, poly2):
    """shapely Polygon IoU"""
    inter = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return inter / union if union > 0 else 0

def toOpen3dCloud(points,colors=None,normals=None):
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points.astype(np.float64))
    if colors is not None:
        if colors.max()>1:
            colors = colors/255.0
        cloud.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
    if normals is not None:
        cloud.normals = o3d.utility.Vector3dVector(normals.astype(np.float64))
    return cloud


def guess_translation(depth, mask, K, debug_dir="", name=""):
    vs, us = np.where(mask > 0)
    if len(us) == 0:
        return np.zeros((3))
    uc = (us.min() + us.max()) / 2.0
    vc = (vs.min() + vs.max()) / 2.0
    valid = mask.astype(bool) & (depth >= 0.001)
    if not valid.any():
        return np.zeros((3))

    zc = np.median(depth[valid])
    center = (np.linalg.inv(K) @ np.asarray([uc, vc, 1]).reshape(3, 1)) * zc
    # pts, colors = depth_to_pointcloud(depth, K, mask)
    # cloud = o3d.geometry.PointCloud()
    # cloud.points = o3d.utility.Vector3dVector(pts.astype(np.float32))
    #
    # pcd = toOpen3dCloud(center.reshape(1, 3))
    # o3d.io.write_point_cloud(f'{debug_dir}/{name}.ply', cloud)
    # o3d.visualization.draw_geometries([pcd])
    return center.reshape(3)

def mask_iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """
    计算两个二值 mask 的 IoU (Intersection over Union)

    Args:
        mask1 (np.ndarray): 二值 mask，元素为 0 或 1
        mask2 (np.ndarray): 二值 mask，元素为 0 或 1

    Returns:
        float: IoU 值，范围 [0,1]
    """
    assert mask1.shape == mask2.shape, "两个mask的尺寸必须一致"

    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()

    if union == 0:
        return 0.0  # 避免除零
    return intersection / union

def load_yolo_to_mask(txt_path, img_w, img_h):
    """读取yolov8 txt segmentation，返回list[Polygon]"""
    masks = []
    with open(txt_path, "r") as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            coords = list(map(float, parts[1:]))
            pts = [(coords[i] * img_w, coords[i+1] * img_h) for i in range(0, len(coords), 2)]
            pts = np.asarray(pts, np.int32).reshape(-1,2)
            cur_mask = np.zeros((img_h, img_w), dtype=np.uint8)
            cv2.fillPoly(cur_mask, [pts], 1)
            masks.append(cur_mask)
    return masks


def depth_to_pointcloud(depth, K, mask=None, depth_scale=1.0, colors=None):
    """
    Convert a depth image to an (N,3) point cloud in camera coordinates.

    Args:
        depth: HxW numpy array (float or uint16) containing depth values.
        K: 3x3 camera intrinsic matrix.
        depth_scale: scale factor to convert depth values to meters
                     (e.g. if depth is in mm, use depth_scale=1000.0).
        mask: optional HxW boolean array that selects which pixels to keep (True = keep).
        colors: optional HxWx3 uint8 array of RGB values.

    Returns:
        points: (N,3) float32 array of 3D points [x,y,z].
        colors_out: (N,3) uint8 array of RGB values, or None.
    """
    assert depth.ndim == 2, "depth must be HxW"
    H, W = depth.shape
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    # pixel grid
    u, v = np.meshgrid(np.arange(W), np.arange(H))
    z = depth.astype(np.float32) / float(depth_scale)

    valid = (z > 0) & np.isfinite(z)
    if mask is not None:
        valid &= mask.astype(bool)

    u, v, z = u[valid], v[valid], z[valid]

    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    points = np.stack((x, y, z), axis=-1).astype(np.float32)

    colors_out = None
    if colors is not None:
        assert colors.shape[:2] == depth.shape
        colors_out = colors[valid].astype(np.uint8)

    return points, colors_out

def mask_to_polygons(mask):
    mask = mask.astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        if len(contour) < 3:
            continue
        contour = contour.squeeze(1)
        pts = [(float(x), float(y)) for x, y in contour]
        poly = Polygon(pts)
        if not poly.is_valid or poly.area < 1:
            continue
        polygons.append(poly)
    return polygons

def load_pose(pose_path, split_class=False):
    poses = []
    with open(pose_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):  # 跳过空行和注释
                continue
            values = list(map(float, line.split()))
            poses.append(values)
    return np.asarray(poses)


def check_depth_pr(gt_depth, pred_depth, mask, abs_rel_threshold=0.02, abs_threshold=0.01):
    """
    计算深度预测的误差指标，包括:
      - abs_rel: mean(|gt - pred| / gt)
      - recall:   (误差 < acc_threshold 的点数) / 有效 GT 点数
      - precision:(误差 < acc_threshold 的点数) / 有效 Pred 点数
    """
    gt = gt_depth[mask > 0].astype(np.float32)
    pred = pred_depth[mask > 0].astype(np.float32)

    valid_gt = (gt > 0) & np.isfinite(gt)
    valid_pred = (pred > 0) & np.isfinite(pred)
    valid = valid_gt & valid_pred

    gt, pred = gt[valid], pred[valid]
    if len(gt) == 0:
        return {"abs_rel": np.nan, "recall": np.nan, "precision": np.nan}

    abs_rel = np.mean(np.abs(gt - pred) / gt)
    
    abs_error_pred = np.mean(np.abs(gt - pred))
    
    err = pred - gt
    err_std = np.std(err)
    
    # max_err = np.max(np.abs(err))
    p95_err = np.percentile(np.abs(err), 95)
    
    median_abs = np.median(np.abs(err))

    # 计算相对误差
    abs_error = np.abs(err)
    rel_error = abs_error / gt
    correct_mask = rel_error < abs_rel_threshold
    abs_correct_mask = abs_error < abs_threshold

    recall = np.sum(correct_mask) / np.sum(valid_gt)
    precision = np.sum(correct_mask) / np.sum(valid_pred)
    

    abs_recall = np.sum(abs_correct_mask) / np.sum(valid_gt)
    abs_precision = np.sum(abs_correct_mask) / np.sum(valid_pred)

    return {"abs_rel": abs_rel, "abs_error": abs_error_pred, "recall": recall, 
            "precision": precision, "abs_recall":abs_recall, "abs_precision": abs_precision,
            "err_std": err_std, "p95_err": p95_err, "median_abs": median_abs}



def check_detph(gt_depth, pred_depth, mask, threshold=0.05):
    gt = gt_depth[mask > 0].astype(np.float32)
    pred = pred_depth[mask > 0].astype(np.float32)
    valid_gt = (gt > 0) & np.isfinite(gt)
    valid_pred = (pred > 0) & np.isfinite(pred)
    valid = valid_gt & valid_pred
    # valid = (gt > 0) & (pred > 0) & np.isfinite(gt) & np.isfinite(pred)
    gt, pred = gt[valid], pred[valid]

    # 常见指标
    mae = np.mean(np.abs(gt - pred))
    rmse = np.sqrt(np.mean((gt - pred)**2))
    abs_rel = np.mean(np.abs(gt - pred) / gt)

    thresh = np.maximum(gt / pred, pred / gt)
    d1 = np.mean(thresh < 1.25)
    coverage = np.sum(valid_pred) / np.sum(valid_gt) if np.sum(valid_gt) > 0 else 0
    # 点云质心差
    # 这里假设你有 (u,v) -> (x,y,z) 投影函数，先生成点云再算
    # 简化写法：直接对深度当成z，算均值差
    centroid_err = abs(np.mean(gt) - np.mean(pred))

    return dict(AbsRel=float(abs_rel),Coverage=float(coverage), MAE=float(mae), RMSE=float(rmse),  δ1=float(d1), CentroidErr=float(centroid_err))



if __name__ == '__main__':

    # test_folder_dir = "/home/ubt/ws/data/sanyi/tmp_val_0916m_0/"
    test_folder_dir = "/home/ubt/ws/data/sanyi/sanyi_val"
    saved_pkls_folder = test_folder_dir + "data"
    sim_depth_folder = test_folder_dir +"depth_sim"
    labels_gt_folder = test_folder_dir  + "labels_gt"
    pose_folder = test_folder_dir + "poses"
    debug_folder = test_folder_dir + "debug"
    K = np.array([[278.930973893, 0.0, 304.0],
                [0.0, 278.930973893, 192.0],
                [0.0, 0.0, 1.0]])
    os.makedirs(debug_folder, exist_ok=True)
    bad_cases = os.listdir(saved_pkls_folder)

    stereo_case = 0
    mask_case = 0
    total_case = 0
    error_stereo = 0
    for bad_case in bad_cases:
        print('-------------------------------------------------------------------------')
        # sample_name =  "rgb_000924_0_20250902_110310_412785"
        name = bad_case.split('.')[0]
        sample_name = name.split('_', 1)[1]
        print(f"Process {bad_case}")
        pkl_name = bad_case
        bad_case_no = bad_case.split("_")[0]
        pkl_path = os.path.join(saved_pkls_folder, pkl_name)
        depth_sim_path = os.path.join(sim_depth_folder, f"{sample_name}.png")
        label_gt_path = os.path.join(labels_gt_folder, f"{sample_name}.txt")
        poses_path = os.path.join(pose_folder, f"{sample_name}.txt")
        debug_path = os.path.join(debug_folder, f"{sample_name}")
        os.makedirs(debug_path, exist_ok=True)

        depth_sim = cv2.imread(depth_sim_path, cv2.IMREAD_UNCHANGED) / 1000.0
        with open(pkl_path, "rb") as f:
            sample = pickle.load(f)

        poses = load_pose(poses_path)
        cur_matched_pose = None

        rgb = sample["rgb"]
        depth = sample["depth"]
        mask = np.asarray(sample["mask"])
        xyz_map = sample["xyz_map"]

        h,w = mask.shape
        gt_masks = load_yolo_to_mask(label_gt_path, w, h)
        # gt_polys = load_yolo_polygon(label_gt_path, w, h)
        # pred_polys = mask_to_polygons(mask)
        # if len(pred_polys) == 0:
        #     print(f"++++++++++++++++++++++++++No valid polygon found for {sample_name}, {bad_case}++++++++++++++++++++")
        #     continue
        # pred_poly = pred_polys[0]
        # if len(pred_polys) != 0:
        #     print("Warning: there are more than one valid mask polygons")

        depth_masked = depth * mask
        depth_sim_masked = depth_sim * mask
        center_stereo = guess_translation(depth, mask, K, debug_dir=debug_path, name=bad_case_no+"_stereo_pred")
        center_sim = guess_translation(depth_sim, mask, K, debug_dir=debug_path, name=bad_case_no+"_sim_pred")

        iou_thresh = 0.5
        gt_poly = None
        best_iou, best_idx = 0, -1
        for i, gt_mask in enumerate(gt_masks):
            iou = mask_iou(mask, gt_mask)
            #iou = compute_iou(pred_poly, gt_poly)
            if iou > best_iou:
                best_iou, best_idx = iou, i
        if best_iou >= iou_thresh and best_idx >= 0:
            # gt_poly = np.array(gt_polys[best_idx].exterior.coords, np.int32)
            gt_mask = gt_masks[best_idx]
        else:
            print(f"++++++++++++++++++++++++WARNING: no valid mask polygon with iou {iou_thresh}+++++++++++++++++")
        print(best_idx)
        cur_matched_pose = poses[best_idx]
        # pred_poly = np.array(pred_poly.exterior.coords, np.int32)
        # print(gt_poly)
        # print(pred_poly)
        # gt_mask = np.zeros((h, w), dtype=np.uint8)
        # pred_mask = np.zeros((h, w), dtype=np.uint8)
        # cv2.fillPoly(gt_mask, [gt_poly], 1)
        # cv2.fillPoly(pred_mask, [pred_poly], 1)

        center_gt = np.array(cur_matched_pose[1:4], dtype=np.float32)

        center_stereo_gt = guess_translation(depth, gt_mask, K, debug_dir=debug_path, name=bad_case_no+"_stereo_gt")
        center_sim_gt = guess_translation(depth_sim, gt_mask, K, debug_dir=debug_path, name=bad_case_no+"_sim_gt")

        error_stereo_pred = np.max(np.abs(center_gt - center_stereo))
        error_sim_pred = np.max(np.abs(center_gt - center_sim))
        error_stereo_gt = np.max(np.abs(center_gt - center_stereo_gt))
        error_gt = np.max(np.abs(center_gt - center_sim_gt))

        if error_gt > 0.03:
            print(f"WARNING: gt depth error, maybe wrong mask matched. {center_gt}")
        print(f"center sim gt is {center_sim_gt}, error sim gt is {error_gt}")
        print(f"center stereo pred is {center_stereo}, error is {error_stereo_pred}")
        print(f"center sim pred is {center_sim}, error is {error_sim_pred}")
        print(f"center stereo gt is {center_stereo_gt}, error is {error_stereo_gt}")
        if error_stereo_gt > 0.05:
            stereo_case += 1
        if error_sim_pred > 0.05:
            mask_case += 1

    print(f"stereo error is {stereo_case}, mask error is {mask_case}")
