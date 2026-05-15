#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re
import pandas as pd

if __name__ == '__main__':
    outer_label_path = r'D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian2\out2'
    filelist_label = os.listdir(outer_label_path)  # 列举文件
    print(filelist_label)
    total_num_file = len(filelist_label)  # label子文件的总数
    print(total_num_file)
    data = {"A": filelist_label}
    dd = pd.DataFrame(data)
    print(dd)
    dd.to_csv(r'D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian2\output_images_1107_radar_speed_index————.csv')
    # for filename1 in filelist_label:
    #     print(filename1)


# import os
# import csv
# from datetime import datetime
#
#
# def export_filenames_to_csv(source_dir, output_csv="file_list.csv", include_metadata=False):
#     """
#     将指定文件夹中的文件名导出到CSV文件
#
#     参数：
#     source_dir: 要扫描的文件夹路径
#     output_csv: 输出CSV文件的路径（默认当前目录下file_list.csv）
#     include_metadata: 是否包含文件元数据（大小、修改时间）
#     """
#     try:
#         # 获取文件列表并过滤掉目录
#         files = []
#         for item in os.listdir(source_dir):
#             full_path = os.path.join(source_dir, item)
#             if os.path.isfile(full_path):
#                 files.append(full_path)
#
#         if not files:
#             print("警告：目标文件夹中没有文件")
#             return
#
#         # 创建CSV文件并写入数据
#         with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
#             writer = csv.writer(csvfile)
#
#             # 写入表头
#             headers = ["文件名"]
#             if include_metadata:
#                 headers += ["文件大小 (字节)", "最后修改时间", "文件类型"]
#             writer.writerow(headers)
#
#             # 写入文件信息
#             for file_path in files:
#                 filename = os.path.basename(file_path)
#                 row = [filename]
#
#                 if include_metadata:
#                     # 获取文件元数据
#                     stat = os.stat(file_path)
#                     file_size = stat.st_size
#                     mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
#                     file_type = os.path.splitext(filename)[1].lower() or "无扩展名"
#
#                     row += [file_size, mod_time, file_type]
#
#                 writer.writerow(row)
#
#         print(f"成功导出 {len(files)} 个文件信息到 {output_csv}")
#
#     except PermissionError:
#         print("错误：没有文件访问权限")
#     except FileNotFoundError:
#         print("错误：指定的文件夹不存在")
#     except Exception as e:
#         print(f"发生未知错误：{str(e)}")
#
#
# if __name__ == "__main__":
#     # 获取用户输入
#     folder_path = input("请输入要扫描的文件夹路径：").strip()
#     output_name = input("请输入输出CSV文件名（留空使用默认file_list.csv）：").strip() or "file_list.csv"
#     add_metadata = input("是否需要包含文件元数据？(y/n)：").lower() == 'y'
#
#     # 执行导出
#     export_filenames_to_csv(
#         source_dir=folder_path,
#         output_csv=output_name,
#         include_metadata=add_metadata
#     )

