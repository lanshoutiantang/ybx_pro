#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2 as cv
import json
import numpy as np
from pathlib import Path
import sys


def load_mat(fs: cv.FileStorage, key: str):
    node = fs.getNode(key)
    if node.empty():
        raise KeyError(f'"{key}" not found in YAML.')
    return node.mat()


def make_rt(R, T_mm):
    """Return 4 × 4 RT with translation converted mm → m."""
    rt = [[float(x) for x in row] + [0.0] for row in R]  # 3×4
    for i in range(3):
        rt[i][3] = float(T_mm[i, 0]) / 1000.0
    rt.append([0.0, 0.0, 0.0, 1.0])
    return rt


def build_dict(yml_path: Path):
    fs = cv.FileStorage(str(yml_path), cv.FILE_STORAGE_READ)
    if not fs.isOpened():
        raise IOError(f"Cannot open {yml_path}")

    version = str(fs.getNode("version").string())
    K1, D1 = load_mat(fs, "K1"), load_mat(fs, "D1").flatten()
    K2, D2 = load_mat(fs, "K2"), load_mat(fs, "D2").flatten()
    R, T = load_mat(fs, "R"), load_mat(fs, "T")  # T in mm
    alpha_stereo_rectify = fs.getNode("alpha_stereo_rectify").real()
    P1 = load_mat(fs, "P1")
    RMS = fs.getNode("RMS").real()
    calibration_time = str(fs.getNode("calibration_time").string())
    fs.release()

    return {
        "version": version,
        "focal_length": float(P1[0, 0]),
        "baseline": abs(float(T[0, 0])) / 1000.0,
        "dilate_ks": 2,
        "use_shmmsgs": True,
        "canny_set": {"edge_min": 20, "edge_max": 50},
        "camL": {
            "fx": float(K1[0, 0]),
            "fy": float(K1[1, 1]),
            "cx": float(K1[0, 2]),
            "cy": float(K1[1, 2]),
            "distortion_coeffs": [float(x) for x in D1],
        },
        "camR": {
            "fx": float(K2[0, 0]),
            "fy": float(K2[1, 1]),
            "cx": float(K2[0, 2]),
            "cy": float(K2[1, 2]),
            "distortion_coeffs": [float(x) for x in D2],
        },
        "RT": make_rt(R, T),
        "alpha_stereo_rectify": float(alpha_stereo_rectify),
        "publish_params": {
            "fx": float(P1[0, 0]),
            "fy": float(P1[1, 1]),
            "cx": float(P1[0, 2]),
            "cy": float(P1[1, 2]),
        },
        "stereo_rms": RMS,
        "stereo_calibration_time": calibration_time,
    }


def write_mat(fs: cv.FileStorage, key: str, mat):
    """Write matrix or scalar into cv::FileStorage"""
    fs.write(name=key, val=np.array(mat))


def convert_json_to_stereo_yml(json_path, yml_path):
    if type(json_path) is not Path:
        json_path = Path(json_path)
    if type(yml_path) is not Path:
        yml_path = Path(yml_path)

    data = json.loads(json_path.read_text())

    camL = data["camL"]
    camR = data["camR"]
    P = data["publish_params"]
    RT = np.array(data["RT"])
    T = RT[:3, 3:] * 1000  # convert back to mm
    R = RT[:3, :3]

    fs = cv.FileStorage(str(yml_path), cv.FILE_STORAGE_WRITE)

    # judge image_size from camL["cx"]
    cx = camL["cx"]
    cx_threshold = 50
    if abs(cx - 960.0) < cx_threshold:
        image_size = np.array([1920.0, 1536.0])
    elif abs(cx - 640.0) < cx_threshold:
        image_size = np.array([1280.0, 720.0])
    else:
        raise ValueError("Unknown image_size.")
    write_mat(fs, "size", image_size)

    write_mat(
        fs,
        "K1",
        np.array(
            [
                [camL["fx"], 0, camL["cx"]],
                [0, camL["fy"], camL["cy"]],
                [0, 0, 1],
            ]
        ),
    )
    write_mat(fs, "D1", np.array(camL["distortion_coeffs"]).reshape(1, -1))

    write_mat(
        fs,
        "K2",
        np.array(
            [
                [camR["fx"], 0, camR["cx"]],
                [0, camR["fy"], camR["cy"]],
                [0, 0, 1],
            ]
        ),
    )
    write_mat(fs, "D2", np.array(camR["distortion_coeffs"]).reshape(1, -1))

    write_mat(fs, "R", R)
    write_mat(fs, "T", T)

    if "alpha_stereo_rectify" in data:
        fs.write("alpha_stereo_rectify", data["alpha_stereo_rectify"])

    write_mat(
        fs,
        "P1",
        np.array(
            [
                [P["fx"], 0, P["cx"], 0],
                [0, P["fy"], P["cy"], 0],
                [0, 0, 1, 0],
            ]
        ),
    )

    if "stereo_rms" in data:
        fs.write("RMS", data["stereo_rms"])
    if "stereo_calibration_time" in data:
        fs.write("calibration_time", data["stereo_calibration_time"])

    fs.release()
    print(f"convert {json_path} to {yml_path} .")


def convert_stereo_yml_to_json(yml_path, json_path):
    if type(yml_path) is not Path:
        yml_path = Path(yml_path)
    if type(json_path) is not Path:
        json_path = Path(json_path)

    params = build_dict(yml_path)
    json_path.write_text(json.dumps(params, indent=2))
    print(f"convert {yml_path} to {json_path}.")


def test_convert_stereo_yml_to_json():
    # 默认路径
    default_in = Path("stereo_cam.yml")
    default_out = Path("stereo_params.json")

    if len(sys.argv) == 1:
        yml_path, json_path = default_in, default_out
    elif len(sys.argv) == 3:
        yml_path = Path(sys.argv[1]).expanduser().resolve()
        json_path = Path(sys.argv[2]).expanduser().resolve()
    else:
        print(
            "Usage:\n"
            "  python yml2json.py              # 默认 ./stereo_cam.yml → ./stereo_params.json\n"
            "  python yml2json.py in.yml out.json",
            file=sys.stderr,
        )
        sys.exit(1)

    convert_stereo_yml_to_json(yml_path, json_path)


def test_convert_json_to_stereo_yml():
    default_in = Path("stereo_params.json")
    default_out = Path("stereo_cam_out.yml")

    if len(sys.argv) == 1:
        json_path, yml_path = default_in, default_out
    elif len(sys.argv) == 3:
        json_path = Path(sys.argv[1]).expanduser().resolve()
        yml_path = Path(sys.argv[2]).expanduser().resolve()
    else:
        print(
            "Usage:\n"
            "  python json2yaml.py              # 默认 ./stereo_params.json → ./stereo_cam_out.yml\n"
            "  python json2yaml.py in.json out.yml",
            file=sys.stderr,
        )
        sys.exit(1)

    convert_json_to_stereo_yml(json_path, yml_path)


if __name__ == "__main__":
    # test_convert_stereo_yml_to_json()

    test_convert_json_to_stereo_yml()
