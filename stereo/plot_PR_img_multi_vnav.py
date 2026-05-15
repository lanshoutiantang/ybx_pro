import os
import matplotlib.pyplot as plt
import numpy as np

def parse_average_from_txt(txt_file):
    with open(txt_file, "r") as f:
        lines = f.readlines()
        if len(lines) == 0:
            return None, None
        last_line = lines[-1]
        if not last_line.startswith("AVERAGE"):
            return None, None
        parts = last_line.strip().split("\t")
        precision = float(parts[1].split("=")[1])
        recall = float(parts[2].split("=")[1])
        return precision, recall

def collect_pr_data(log_dir):
    ks_dirs = sorted([d for d in os.listdir(log_dir) if d.startswith("ks_")])
    overall_precision = []
    overall_recall = []
    ks_values = []
    for ks_dir in ks_dirs:
        ks_val = int(ks_dir.split("_")[1])
        ks_values.append(ks_val)
        ks_path = os.path.join(log_dir, ks_dir)
        overall_txt = os.path.join(ks_path, "overall_pr.txt")
        p, r = parse_average_from_txt(overall_txt)
        overall_precision.append(p)
        overall_recall.append(r)
    return ks_values, overall_precision, overall_recall

def plot_multi_dirs(log_dirs, labels, save_path):
    plt.figure(figsize=(8,6))
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'brown', 'gray'] # 可扩展

    for idx, log_dir in enumerate(log_dirs):
        ks_values, precision, recall = collect_pr_data(log_dir)

        # 计算合理的纵向偏移，避免数字贴在线上
        r_min, r_max = min(recall), max(recall)
        offset = 0.02 * (r_max - r_min)

        plt.plot(precision, recall, marker='o', color=colors[idx], label=labels[idx])
        # for i, ks in enumerate(ks_values):
        #     plt.text(precision[i], recall[i]+offset, str(ks), fontsize=7, ha='center', color=colors[idx])
    
    # xlim = [0.5, 0.95]
    # ylim = [0.7, 0.95]
          
    # if xlim is not None:
    #     plt.xlim(xlim)
    # if ylim is not None:
    #     plt.ylim(ylim)

    plt.xlabel("Precision")
    plt.ylabel("Recall")
    plt.title("Overall PR vs ks")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"保存对比图到 {save_path}")


# 仅修改main函数，实现「分组绘制」逻辑
if __name__ == "__main__":
    # 基础配置
    base_log_path = "D:\Program Files\JetBrains\pythonProject\stereo\pr_test1"
    save_root_dir = "./multi_subdir_plots"
    os.makedirs(save_root_dir, exist_ok=True)  # 自动创建保存目录

    # 定义分组的子目录列表：嵌套列表表示一组，字符串表示单独目录
    level2_dirs = ["navigate","navigate_back", "navigate_head", "navigate_waist"]  # 这三个归为一组
    # level2_dirs = ["navigate",]

    # 版本列表
    versions = [
        # dark系列
        # "s012_1920_shadow",
        # "s015_1920_shadow",
        # "s018_1920_new_shadow",
        # "s019_1920_new_shadow"

        # "s019_1920",
        # "s019_weak-mining-qat_1920",
        #
        # "s019_1280",
        # "s019_weak-mining-qat_1280"

        # "s012",
        # "s015",
        # "s018_1280",
        # "s019_1280",
        # "s0110_1280",
        # "s0111_1280",
        # "1280/s0110",
        # "1280/s0110-weak-mining-qat",
        # "1920/s0110",
        # "1920/s0110-weak-mining-qat",

        # "s019_1280",
        # "s019_1920",
        # "s019_weak-mining-qat_1280",
        # "s019_weak-mining-qat_1920",
        # "s0.1.9_mining_gama1.05_1280",
        # "s0.1.9_mining_gama1.05_1920",

        # "s019_1280",
        # "s019_1920",
        # "s0.1.9_mono_1280",
        # "s0.1.9_mono_1920",
        # "s0.1.11_mono_navigate_hecheng",
        # "s019_1280",
        # "s019_1920",
        # "s0.1.9_mono_1280",
        # "s0.1.9_mono_1920",
        "s0.1.14_origin_1280",
        "s0.1.14_origin_1920",
        "s0.1.14_dla_1280",
        "s0.1.14_dla_1920",
        "s0.1.14_1280",
        "s0.1.14_1920",
    ]

    # 遍历每个目录/目录组
    for item in level2_dirs:
        # 存储当前组的所有日志路径和标签
        group_log_dirs = []
        group_labels = []

        # 处理「单独目录」（字符串类型）
        if isinstance(item, str):
            sub_dir = item
            # 遍历版本，收集该目录的所有版本数据
            for ver_dir in versions:
                # full_log_path = os.path.join(base_log_path, ver_dir, sub_dir+"_"+ver_dir)
                full_log_path = os.path.join(base_log_path, ver_dir, sub_dir)
                if os.path.exists(full_log_path):
                    group_log_dirs.append(full_log_path)
                    group_labels.append(f"{ver_dir}_{sub_dir}")
            # 生成图片名：pr_单独目录名.png
            save_name = f"pr_{sub_dir}.png"

        # 处理「目录组」（列表类型）
        elif isinstance(item, list):
            group_name = "navigate_group"  # 给分组命名（可自定义）
            # 遍历分组内的每个子目录 + 所有版本
            for sub_dir in item:
                for ver_dir in versions:
                    full_log_path = os.path.join(base_log_path, ver_dir, sub_dir)
                    if os.path.exists(full_log_path):
                        group_log_dirs.append(full_log_path)
                        group_labels.append(f"{ver_dir}_{sub_dir}")
            # 生成图片名：pr_分组名.png
            save_name = f"pr_{group_name}.png"

        # 跳过无有效数据的组/目录
        if not group_log_dirs:
            print(f"⚠️ {item} 无有效数据，跳过")
            continue

        # 拼接最终保存路径并绘图
        save_path = os.path.join(save_root_dir, save_name)
        plot_multi_dirs(group_log_dirs, group_labels, save_path)