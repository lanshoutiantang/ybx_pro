import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
from matplotlib import rcParams

def set_chinese_font():
    """设置中文字体，解决中文显示问题"""
    try:
        rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
        rcParams['axes.unicode_minus'] = False
    except:
        print("警告: 中文字体设置失败，图表可能无法正常显示中文")

def process_files(file_pattern, min_samples=2000):
    """处理CSV文件并返回统计数据"""
    files = sorted(glob.glob(file_pattern))  # 排序文件以确保顺序
    if not files:
        print("未找到匹配的CSV文件")
        return None
    
    all_data = []
    cumulative_count = 0  # 累计样本计数
    
    for file in files:
        try:
            df = pd.read_csv(file)
            if len(df) >= min_samples:
                vel_y = df['vel_y']
                
                # 创建连续索引
                start_idx = cumulative_count
                end_idx = start_idx + len(vel_y)
                indices = range(start_idx, end_idx)
                
                stats = {
                    'filename': os.path.basename(file),
                    'sample_count': len(df),
                    'start_idx': start_idx,
                    'end_idx': end_idx,
                    'mean': vel_y.mean(),
                    'max': vel_y.max(),
                    'min': vel_y.min(),
                    'std': vel_y.std(),
                    'p_gt_0.01': (vel_y > 0.01).mean(),
                    'p_gt_0.02': (vel_y > 0.02).mean(),
                    'vel_y_data': vel_y.values,
                    'indices': indices
                }
                
                all_data.append(stats)
                cumulative_count = end_idx  # 更新累计计数
                print(f"处理成功: {os.path.basename(file)} (样本: {len(df)}), 全局索引: {start_idx}-{end_idx-1}")
            else:
                print(f"跳过: {os.path.basename(file)} (样本不足: {len(df)} < {min_samples})")
                
        except Exception as e:
            print(f"处理失败 {os.path.basename(file)}: {str(e)}")
    
    return all_data if all_data else None

def plot_continuous_data(data):
    """绘制连续数据折线图"""
    if not data:
        print("没有足够的数据进行绘图")
        return
    
    plt.figure(figsize=(15, 8))
    set_chinese_font()
    
    # 绘制所有文件的连续数据
    for i, stats in enumerate(data):
        # 使用不同的颜色
        color = plt.cm.tab10(i % 10)
        plt.plot(stats['indices'], stats['vel_y_data'], 
                color=color, alpha=0.7, 
                label=f"{stats['filename']} (样本: {stats['sample_count']})")
        
        # 标记文件分界点
        if i > 0:
            plt.axvline(x=stats['start_idx'], color='gray', linestyle=':', alpha=0.5)
    
    # 添加参考线
    plt.axhline(y=0.01, color='r', linestyle='--', alpha=0.5, label='0.01参考线')
    plt.axhline(y=0.02, color='g', linestyle='--', alpha=0.5, label='0.02参考线')
    
    # 设置图表属性
    plt.title('vel_y数据连续趋势图 (多文件合并)', fontsize=16)
    plt.xlabel('全局样本序号', fontsize=12)
    plt.ylabel('vel_y值', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 自动调整布局
    plt.tight_layout()
    
    # 保存图表
    plt.savefig('vel_y_continuous_plot.png', dpi=300, bbox_inches='tight')
    print("\n连续趋势图已保存为 vel_y_continuous_plot.png")
    plt.close()

def generate_statistics_report(data):
    """生成统计报告"""
    if not data:
        return
    
    report_data = []
    for stats in data:
        report_data.append({
            '文件名': stats['filename'],
            '样本数量': stats['sample_count'],
            '起始索引': stats['start_idx'],
            '结束索引': stats['end_idx']-1,
            '平均值': stats['mean'],
            '最大值': stats['max'],
            '最小值': stats['min'],
            '标准差': stats['std'],
            '>0.01概率': stats['p_gt_0.01'],
            '>0.02概率': stats['p_gt_0.02']
        })
    
    report_df = pd.DataFrame(report_data)
    
    # 保存CSV
    report_df.to_csv('vel_y_statistics_report.csv', index=False, encoding='utf_8_sig')
    
    # 打印报告
    print("\n统计报告:")
    print(report_df.to_string(index=False))
    print("\n详细报告已保存为 vel_y_statistics_report.csv")

if __name__ == "__main__":
    # 设置全局样式
    rcParams['figure.facecolor'] = 'white'
    
    # 文件匹配模式（可根据需要修改）
    file_pattern = r"D:\control_debug\2025-*.csv"
    
    print("开始处理文件...")
    processed_data = process_files(file_pattern, min_samples=2000)
    
    if processed_data:
        print("\n生成连续趋势图...")
        plot_continuous_data(processed_data)
        
        print("\n生成统计报告...")
        generate_statistics_report(processed_data)
        
        print("\n分析完成！")
    else:
        print("没有可分析的数据")
