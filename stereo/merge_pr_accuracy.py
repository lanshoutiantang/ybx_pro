import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

# ===================== 可配置参数 =====================

ROOT_DIRS = [
    "D:\Program Files\JetBrains\pythonProject\stereo\pr_test",
    # "D:\Program Files\JetBrains\pythonProject\stereo\pr_test\s0.1.11_mono",
]

KS_NAME = "ks_2"
PR_FILENAME = "overall_pr.txt"

SCENE_MAP = {
    "carry": "carry",
    # "carry_s0.1.9_mono_1280": "carry",
    "carry_head": "carry",
    "carry_waist": "carry",

    "carry_shiyan": "carry_shiyan",
    # "carry_shiyan_s0.1.9_mono_1280": "carry_shiyan",

    "sps": "sps",
    # "sps_s0.1.9_mono_1280": "sps",
    "sps_head": "sps",
    # "sps_liuqi": "sps",
    # "sps_liuqi_multi": "sps",
    # "sps_sanyi": "sps",

    "navigate": "navigate",
    # "navigate_s0.1.9_mono_1280": "navigate",
    "navigate_head": "navigate",
    "navigate_back": "navigate",
    "navigate_waist": "navigate",
}

# ===================== 版本排序函数 =====================

def version_key(v):
    """
    s0.1.11m_0.01 → 可排序key
    """
    nums = re.findall(r'\d+', v)
    return tuple(int(x) for x in nums)


# ===================== 解析PR文件 =====================

def parse_overall_pr(file_path):
    with open(file_path, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    last = lines[-1]

    def get_val(key):
        m = re.search(rf"{key}=([0-9.]+)", last)
        return float(m.group(1)) if m else 0.0

    return {
        "correct": get_val("correct"),
        "valid_pred": get_val("valid_pred"),
        "gt_mask": get_val("gt_mask"),
    }


# ===================== 聚合统计 =====================

stats = defaultdict(lambda: defaultdict(lambda: {
    "correct": 0.0,
    "valid_pred": 0.0,
    "gt_mask": 0.0
}))

for root in ROOT_DIRS:
    for version in os.listdir(root):
        version_dir = os.path.join(root, version)
        if not os.path.isdir(version_dir):
            continue

        for scene in os.listdir(version_dir):

            if scene not in SCENE_MAP:
                continue

            task = SCENE_MAP[scene]

            pr_path = os.path.join(
                version_dir,
                scene,
                KS_NAME,
                PR_FILENAME
            )

            if not os.path.exists(pr_path):
                print("missing:", pr_path)
                continue

            data = parse_overall_pr(pr_path)

            stats[version][task]["correct"] += data["correct"]
            stats[version][task]["valid_pred"] += data["valid_pred"]
            stats[version][task]["gt_mask"] += data["gt_mask"]


# ===================== 计算PR =====================

results = defaultdict(dict)

for version in stats:
    for task in stats[version]:
        s = stats[version][task]

        if s["valid_pred"] == 0 or s["gt_mask"] == 0:
            continue

        P = s["correct"] / s["valid_pred"]
        R = s["correct"] / s["gt_mask"]

        results[version][task] = (P, R)


# ===================== 按版本排序 =====================

versions_sorted = sorted(results.keys(), key=version_key)

print("\n========== 聚合结果 ==========\n")

for v in versions_sorted:
    print(f"{v}")
    for task in ["carry", "sps", "navigate", "carry_shiyan"]:
        if task in results[v]:
            P, R = results[v][task]
            print(f"  {task:8s}  P={P:.6f}  R={R:.6f}")
        else:
            print(f"  {task:8s}  无数据")
    print()


print("DEBUG: stats keys:", list(stats.keys()))
print("DEBUG: results keys:", list(results.keys()))
