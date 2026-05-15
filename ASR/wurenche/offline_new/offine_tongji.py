import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.ticker import MaxNLocator


def extract_data_from_file(file_path):
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Extract class AP data
    class_pattern = re.compile(
        r'\|.*?\d+\s+\|\s+(.*?)\s+\|\s+([\d\.]*)\s*\|\s+([\d\.]*)\s*\|\s+([\d\.]*)\s*\|\s+([\d\.]*)\s*\|\s+([\d\.]*)\s*\|\s+([\d\.]*)')
    class_matches = class_pattern.findall(content)

    class_data = {
        'class': [],
        'ap@0.5[0,10]': [],
        'ap@0.5[10,20]': [],
        'ap@0.5[20,30]': [],
        'ap@0.5[30,40]': [],
        'ap@0.5[40,50]': [],
        'ap@0.5[50,inf]': []
    }

    for match in class_matches:
        class_data['class'].append(match[0].strip())
        for i in range(1, 7):
            val = match[i].strip()
            class_data[list(class_data.keys())[i]].append(float(val) if val else None)

    # Extract metrics data
    metrics_pattern = re.compile(
        r'\|.*?mAP\[(.*?)\]\s+\|\s+mATE\[.*?\]\s+\|\s+mASE\[.*?\]\s+\|\s+mAOE\[.*?\]\s+\|\s+NDS\[.*?\]\s+\|\s+\|\s+([\d\.]+)\s+\|\s+([\d\.]+)\s+\|\s+([\d\.]+)\s+\|\s+([\d\.]+)\s+\|\s+([\d\.]+)')
    metrics_matches = metrics_pattern.findall(content)

    metrics_data = {
        'distance_ranges': [],
        'mAP': [],
        'mATE': [],
        'mASE': [],
        'mAOE': [],
        'NDS': []
    }

    for match in metrics_matches:
        metrics_data['distance_ranges'].append(f'[{match[0]}]')
        metrics_data['mAP'].append(float(match[1]))
        metrics_data['mATE'].append(float(match[2]))
        metrics_data['mASE'].append(float(match[3]))
        metrics_data['mAOE'].append(float(match[4]))
        metrics_data['NDS'].append(float(match[5]))

    return class_data, metrics_data


# File path to your data
file_path = 'D:\Program Files\JetBrains\pythonProject\ASR\wurenche\offline_new\offline_mix3_1.2.2_nex.txt'

# Extract data from file
class_data, metrics_data = extract_data_from_file(file_path)

# Create figure
plt.figure(figsize=(20, 10))

# ================= First Subplot: Class AP Values =================
plt.subplot(1, 2, 1)

# Distance range labels and colors
distance_ranges = ['[0,10]', '[10,20]', '[20,30]', '[30,40]', '[40,50]', '[50,inf]']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# Plot AP values for each distance range
for i, range_key in enumerate([key for key in class_data.keys() if key != 'class']):
    ap_values = class_data[range_key]
    # Replace None with 0 for plotting
    cleaned_ap = [0 if v is None else v for v in ap_values]
    plt.plot(class_data['class'], cleaned_ap,
             marker='o',
             label=f'AP@0.5{distance_ranges[i]}',
             color=colors[i],
             linewidth=2,
             markersize=6)

# Chart formatting
plt.title('AP@0.5 by Class and Distance Range', fontsize=14, pad=20)
plt.xlabel('Class', fontsize=12, labelpad=10)
plt.ylabel('Average Precision (AP)', fontsize=12, labelpad=10)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.ylim(-0.05, 1.05)
plt.grid(True, linestyle='--', alpha=0.5)

# ================= Second Subplot: Metrics Trends =================
plt.subplot(1, 2, 2)

# Colors and markers for metrics
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
markers = ['o', 's', '^', 'D', 'v']
metric_labels = ['mAP', 'mATE', 'mASE', 'mAOE', 'NDS']

# Plot each metric
for i, metric in enumerate(metric_labels):
    plt.plot(metrics_data['distance_ranges'], metrics_data[metric],
             marker=markers[i],
             color=colors[i],
             linewidth=2,
             markersize=8,
             label=metric)

# Chart formatting
plt.title('Performance Metrics by Distance Range', fontsize=14, pad=20)
plt.xlabel('Distance Range (meters)', fontsize=12, labelpad=10)
plt.ylabel('Metric Value', fontsize=12, labelpad=10)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.ylim(0, 1.1)
plt.grid(True, linestyle='--', alpha=0.5)

# Adjust layout and save
plt.tight_layout()
plt.savefig('offline_mix3_metrics.png', dpi=300, bbox_inches='tight')
plt.show()