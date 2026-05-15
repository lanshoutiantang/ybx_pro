import os
import shutil


def distribute_files(source_dir, num_folders=10):
    # 获取所有文件（排除目录和自身生成的文件夹）
    files = [f for f in os.listdir(source_dir)
             if os.path.isfile(os.path.join(source_dir, f))]

    if not files:
        print("源文件夹中没有文件。")
        return

    total_files = len(files)
    per_folder, remainder = divmod(total_files, num_folders)

    # 创建目标文件夹
    target_dirs = []
    for i in range(1, num_folders + 1):
        folder_name = os.path.join(source_dir, f"group_{i:02d}")
        os.makedirs(folder_name, exist_ok=True)
        target_dirs.append(folder_name)

    # 分配并移动文件
    count = 0
    for i, folder in enumerate(target_dirs):
        start = count
        end = count + (per_folder + 1 if i < remainder else per_folder)

        for filename in files[start:end]:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(folder, filename)
            shutil.move(src, dst)

        count = end

    print(f"已将 {total_files} 个文件分配到 {num_folders} 个文件夹中")
    print(f"每个文件夹包含 {per_folder} 或 {per_folder + 1} 个文件")


if __name__ == "__main__":
    # source_directory = input(r"D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian1\stereo_data4_-jian1").strip()
    source_directory = r"D:\桌面\UBT\2025\双目\1.0.3\stereo_data4_-jian2\out3 - 副本"
    distribute_files(source_directory)