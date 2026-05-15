#!/usr/bin/env python3
import argparse
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="GPU 数据直方图统计工具（中文显示）")

    parser.add_argument("--input", type=str, default="gpu.data",
                        help="GPU 数据文件路径")
    parser.add_argument("--bins", type=int, default=10,
                        help="等分区间数量 n")
    parser.add_argument("--output", type=str, default="hist.png",
                        help="输出图像文件名")

    return parser.parse_args()

def main():
    args = parse_args()

    # 读取数据python
    with open(args.input, "r") as f:
        raw = f.read().strip().split()
        data = np.array([float(x) for x in raw])

    # ========= 新增：求和 & 均值（避免溢出） =========
    safe_sum = sum(data)              # Python 内置，永不溢出
    mean_val = safe_sum / len(data)   # 均值

    print(f"数据数量: {len(data)}")
    print(f"总和 (Sum): {safe_sum}")
    print(f"均值 (Mean): {mean_val}")

    # 最大最小值
    min_val, max_val = data.min(), data.max()
    print(f"最小值: {min_val}, 最大值: {max_val}")

    # 区间统计
    bins = args.bins
    hist, bin_edges = np.histogram(data, bins=bins, range=(min_val, max_val))

    # 占比计算
    total = len(data)
    ratio = hist / total

    print("\n=== 区间占比统计 ===")
    for i in range(bins):
        print(f"[{bin_edges[i]:.2f}, {bin_edges[i+1]:.2f}]: "
              f"数量={hist[i]}  占比={ratio[i]*100:.2f}%")

    # 绘制中文图表
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(10, 6))

    width = (max_val - min_val) / bins
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    plt.bar(centers, ratio, width=width*0.9)

    plt.xlabel("数值区间", fontsize=14)
    plt.ylabel("占比（Ratio）", fontsize=14)
    plt.title(f"GPU 数据分布直方图（{bins} 个区间）", fontsize=16)

    plt.grid(axis="y", linestyle="--", alpha=0.6)

    plt.savefig(args.output, dpi=150)
    print(f"\n图像已保存到：{args.output}")

if __name__ == "__main__":
    main()
