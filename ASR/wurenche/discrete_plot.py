import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from matplotlib import rcParams


def set_chinese_font():
    """设置中文字体"""
    try:
        rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        rcParams['axes.unicode_minus'] = False
    except:
        print("警告: 中文字体设置失败")


def load_and_filter_files(file_pattern, min_samples=2000):
    """加载并筛选文件"""
    files = sorted(glob.glob(file_pattern))
    valid_files = []
    cumulative_index = 0

    for file in files:
        try:
            df = pd.read_csv(file)
            if len(df) > min_samples:
                valid_files.append({
                    'name': os.path.basename(file),
                    'data': df['vel_y'],
                    'start': cumulative_index,
                    'end': cumulative_index + len(df)
                })
                cumulative_index += len(df)
                print(f"已加载: {os.path.basename(file)} 样本数: {len(df)}")
            else:
                print(f"跳过: {os.path.basename(file)} 样本不足")
        except Exception as e:
            print(f"加载失败 {file}: {str(e)}")

    return valid_files


def plot_discrete_points(data):
    """绘制离散点图"""
    plt.figure(figsize=(15, 8))
    set_chinese_font()

    # 创建颜色映射
    colors = plt.cm.tab10(np.linspace(0, 1, len(data)))

    # 绘制所有数据点
    for i, file_data in enumerate(data):
        x = range(file_data['start'], file_data['end'])
        plt.scatter(x, file_data['data'],
                    s=5,  # 点大小
                    alpha=0.5,
                    color=colors[i],
                    label=f"{file_data['name']} ({len(file_data['data'])}样本)")

        # 添加文件分界线
        if i > 0:
            plt.axvline(x=file_data['start'],
                        color='gray',
                        linestyle=':',
                        linewidth=1,
                        alpha=0.5)

    # 添加参考线
    plt.axhline(0.01, color='r', linestyle='--', alpha=0.7, label='0.01参考线')
    plt.axhline(0.02, color='g', linestyle='--', alpha=0.7, label='0.02参考线')

    # 设置坐标轴
    plt.title('vel_y数据离散点分布（多文件合并）', fontsize=16)
    plt.xlabel('全局样本序号', fontsize=12)
    plt.ylabel('vel_y值', fontsize=12)
    plt.grid(True, alpha=0.2)

    # 优化图例
    legend = plt.legend(bbox_to_anchor=(1.05, 1),
                        loc='upper left',
                        markerscale=3,  # 放大图例中的标记
                        framealpha=0.9)

    # 优化布局
    plt.tight_layout()

    # 保存图片
    plt.savefig('vel_y_discrete_points.png',
                dpi=300,
                bbox_inches='tight')
    print("图表已保存为 vel_y_discrete_points.png")
    plt.close()


def generate_stat_report(data):
    """生成统计报告"""
    report = []
    for file_data in data:
        stats = {
            '文件名': file_data['name'],
            '起始索引': file_data['start'],
            '结束索引': file_data['end'] - 1,
            '样本数': len(file_data['data']),
            '平均值': np.mean(file_data['data']),
            '最大值': np.max(file_data['data']),
            '标准差': np.std(file_data['data']),
            '>0.01比例': np.mean(file_data['data'] > 0.01),
            '>0.02比例': np.mean(file_data['data'] > 0.02)
        }
        report.append(stats)

    df = pd.DataFrame(report)
    df.to_csv('vel_y_stat_report.csv', index=False, encoding='utf_8_sig')
    print("\n统计报告:")
    print(df.to_string(index=False))
    print("详细报告已保存为 vel_y_stat_report.csv")


if __name__ == "__main__":
    # 配置参数
    rcParams['figure.facecolor'] = 'white'
    FILE_PATTERN = r"D:\control_debug\2025-*.csv"

    print("开始处理文件...")
    valid_data = load_and_filter_files(FILE_PATTERN, min_samples=2000)

    if valid_data:
        print("\n生成离散点图...")
        plot_discrete_points(valid_data)

        print("\n生成统计报告...")
        generate_stat_report(valid_data)

        print("\n处理完成！")
    else:
        print("没有找到有效数据")