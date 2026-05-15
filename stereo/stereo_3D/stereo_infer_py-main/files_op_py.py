import fnmatch
import os
import re
import shutil


def copy_files_by_prefix(directory, save_dir="./"):
    # 获取目录中的所有文件
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]

    # 创建一个字典来存储前缀和对应的文件列表
    prefix_dict = {}

    for file in files:
        # 获取文件名和扩展名
        filename, file_extension = os.path.splitext(file)

        # 获取前缀（以_划分的部分）
        if "_" in filename:
            prefix = filename.split("_")[0]
        else:
            prefix = filename  # 如果没有_，则整个文件名作为前缀

        # 如果前缀不在字典中，则创建一个新条目
        if prefix not in prefix_dict:
            prefix_dict[prefix] = []

        # 将文件添加到对应前缀的列表中
        prefix_dict[prefix].append(file)

    # 遍历字典，创建子目录并将文件移动到相应的子目录中
    for prefix, file_list in prefix_dict.items():
        # 创建子目录
        subdirectory = os.path.join(save_dir, prefix)
        os.makedirs(subdirectory, exist_ok=True)

        # 拷贝文件到子目录
        for file in file_list:
            src_path = os.path.join(directory, file)
            dst_path = os.path.join(subdirectory, file)
            shutil.copy(src_path, dst_path)
            print(f"Copy {file} to {subdirectory}")


def copy_file(file_name, folder_name):
    if os.path.exists(file_name):
        shutil.copy(file_name, folder_name)
        print("copy file " + file_name + " to " + folder_name + " succeed")
    else:
        print("**** error **** copy file " + file_name + " failed")


def copy_and_rename_file(src_path, dst_dir, new_name):
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, new_name)
    if os.path.exists(dst_path):
        print("**** error ****: dst_path exists")
        return
    shutil.copy2(src_path, dst_path)
    print("copy file " + src_path + " to " + dst_dir + " succeed")


def copy_folder(folder_before, folder_after):  ## folder_after does not exist
    if os.path.exists(folder_after):
        shutil.rmtree(folder_after)

    if os.path.exists(folder_before):
        shutil.copytree(folder_before, folder_after)
        print("copy dir " + folder_before + " to " + folder_after + " succeed")
    else:
        print("**** error **** copy folder " + folder_before + " failed")


def copy_files(src_dir, dest_dir, pattern):
    # 创建目标目录，如果不存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 遍历源目录及其子目录
    for root, dirs, files in os.walk(src_dir):
        for filename in fnmatch.filter(files, pattern):
            # 构建源文件路径
            src_file = os.path.join(root, filename)
            # 构建目标文件路径
            dest_file = os.path.join(dest_dir, filename)
            # 复制文件
            shutil.copy2(src_file, dest_file)
            print(f"Copied: {src_file} to {dest_file}")


def get_file_paths(src_dir, pattern):
    src_files = []
    try:
        for filename in os.listdir(src_dir):
            file_path = os.path.join(src_dir, filename)
            if os.path.isfile(file_path) and fnmatch.fnmatch(filename, pattern):
                src_files.append(file_path)
    except FileNotFoundError:
        print(f"目录 {src_dir} 不存在")
    except PermissionError:
        print(f"没有权限访问目录 {src_dir}")

    return src_files


def get_file_paths_recusively(src_dir, pattern):
    src_files = []
    for root, dirs, files in os.walk(src_dir):
        for filename in fnmatch.filter(files, pattern):
            src_file = os.path.join(root, filename)
            src_files.append(src_file)

    return src_files


def get_relative_paths(directory):
    """
    获取指定目录及其子目录中所有文件的相对路径
    """
    relative_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            relative_path = relative_path.replace("\\", "/")
            relative_paths.append(relative_path)
    return relative_paths


def get_folders_with_pattern(root_dir, pattern):
    """
    查找包含指定模式的文件夹

    参数:
    root_dir: 要搜索的根目录
    pattern: 要查找的模式（正则表达式字符串）

    返回:
    找到的文件夹路径列表
    """
    matched_folders = []

    # 遍历目录树
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and re.match(pattern, item):
            matched_folders.append(item_path)

    return matched_folders


def get_folders_with_pattern_recursively(root_dir, pattern):
    """
    查找包含指定模式的文件夹

    参数:
    root_dir: 要搜索的根目录
    pattern: 要查找的模式（正则表达式字符串）

    返回:
    找到的文件夹路径列表
    """
    matched_folders = []

    # 遍历目录树
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 检查当前目录中的文件夹
        for dirname in dirnames:
            if re.match(pattern, dirname):
                full_path = os.path.join(dirpath, dirname)
                matched_folders.append(full_path)

    return matched_folders


def get_subdirectories(directory):
    subdirectories = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
    return subdirectories


def get_specific_directory(parent_dir, prefix):
    # 遍历指定目录下的所有文件和目录
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        # 检查是否为目录且名称以 'abc' 开头
        if os.path.isdir(item_path) and item.startswith(prefix):
            return item_path
    return None


def get_specific_suffix_file(parent_dir, prefix, exclude_word):
    # 遍历指定目录下的所有文件和目录
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        # 检查是否为文件且名称以 'prefix' 结尾，且不含禁止词
        if (
            os.path.isfile(item_path)
            and item.endswith(prefix)
            and exclude_word not in item
        ):
            return item_path
    return None


def move_file(file_name, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f'create folder "{folder_name}"')

    target_file_path = os.path.join(folder_name, os.path.basename(file_name))

    shutil.move(file_name, target_file_path)


def move_folder(folder_before, folder_after):
    if os.path.abspath(folder_before) == os.path.abspath(
        os.path.join(folder_after, folder_before)
    ):
        print("folder_before and folder_after are the same, no need to move")
        return

    shutil.move(folder_before, folder_after)


def move_folder_contents(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)

        shutil.move(src_item, dst_item)


def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        print("delete " + file_name)
    else:
        print(file_name + " does not exist, no need to delete")


def delete_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
        print("delete " + folder_name)
    else:
        print(folder_name + " does not exist, no need to delete")


def rename_folders_by_mapping(directory, mapping):
    # 遍历目录中的所有文件夹
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)

        # 检查是否是文件夹
        if os.path.isdir(folder_path):
            # 检查文件夹名称是否在映射表中
            if folder_name in mapping:
                new_folder_name = mapping[folder_name]
                new_folder_path = os.path.join(directory, new_folder_name)

                # 重命名文件夹
                os.rename(folder_path, new_folder_path)
                print(f"Renamed '{folder_name}' to '{new_folder_name}'")
            else:
                print(f"Folder '{folder_name}' not found in mapping, skipping.")


def rename_files_by_mapping(directory, mapping):
    # 遍历目录中的所有文件
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # 检查是否是文件（而不是文件夹）
        if os.path.isfile(file_path):
            # 检查文件名称是否在映射表中
            if file_name in mapping:
                new_file_name = mapping[file_name]
                new_file_path = os.path.join(directory, new_file_name)

                # 重命名文件
                os.rename(file_path, new_file_path)
                print(f"Renamed '{file_name}' to '{new_file_name}'")
            else:
                print(f"File '{file_name}' not found in mapping, skipping.")


def rename_files(directory, old_prefix, new_prefix):
    # 遍历目录中的所有文件
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # 检查是否是文件（而不是文件夹）
        if os.path.isfile(file_path):
            # 检查文件名是否以旧前缀开头
            if file_name.startswith(old_prefix):
                # 构造新的文件名
                new_file_name = new_prefix + file_name[len(old_prefix) :]
                new_file_path = os.path.join(directory, new_file_name)

                # 重命名文件
                os.rename(file_path, new_file_path)
                print(f"Renamed '{file_name}' to '{new_file_name}'")


def organize_by_prefix(source_dir):
    """
    根据文件名或文件夹名的第一个前缀进行分类。
    :param source_dir: 要整理的目录路径
    """
    # 遍历源目录中的所有文件和文件夹
    for entry in os.listdir(source_dir):
        entry_path = os.path.join(source_dir, entry)

        # 获取文件名或文件夹名的第一个前缀
        if "_" in entry:
            prefix = entry.split("_")[0]
        else:
            continue  # 如果名称中没有 "_"，跳过

        # 创建目标文件夹路径
        target_dir = os.path.join(source_dir, prefix)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 移动文件或文件夹到目标文件夹
        try:
            shutil.move(entry_path, target_dir)
            print(f"Moved '{entry}' to '{target_dir}'")
        except Exception as e:
            print(f"Error moving '{entry}': {e}")


def add_prefix_to_ith_image(source_folder, destination_folder, prefix, i):
    # 确保目标文件夹存在
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 获取源文件夹中的所有文件
    files = os.listdir(source_folder)

    # 遍历所有文件
    for index, file_name in enumerate(files):
        # 获取文件的完整路径
        source_file_path = os.path.join(source_folder, file_name)

        # 检查文件是否为图像文件（这里假设图像文件的扩展名为 .jpg 或 .png）
        if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
            # 找到第 i 个文件
            if (index // 2) == i:  # Attention
                # 生成新的文件名
                new_file_name = f"{prefix}{file_name}"
                destination_file_path = os.path.join(destination_folder, new_file_name)
            else:
                # 其他文件保持原样
                destination_file_path = os.path.join(destination_folder, file_name)

            # 复制文件到目标文件夹
            shutil.copy2(source_file_path, destination_file_path)
            print(f"Copied {file_name} to {destination_file_path}")


def compare_and_move_files(src_dir, compare_dir, dest_dir):
    """
    比较两个文件夹，将第一个文件夹中有而第二个文件夹中没有的文件剪切到第三个文件夹。

    :param src_dir: 第一个文件夹路径
    :param compare_dir: 第二个文件夹路径
    :param dest_dir: 第三个文件夹路径
    """
    # 确保输出目录存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 获取两个文件夹的文件名集合
    src_files = set(os.listdir(src_dir))
    compare_files = set(os.listdir(compare_dir))

    # 找出第一个文件夹中有而第二个文件夹中没有的文件
    files_to_move = src_files - compare_files

    # 剪切这些文件到目标文件夹
    for file in files_to_move:
        src_file_path = os.path.join(src_dir, file)
        dest_file_path = os.path.join(dest_dir, file)

        # 确保是文件（排除子目录）
        if os.path.isfile(src_file_path):
            shutil.move(src_file_path, dest_file_path)
            print(f"Moved: {src_file_path} -> {dest_file_path}")
        else:
            print(f"Skipped (not a file): {src_file_path}")


if __name__ == "__main__":
    # 输入文件夹路径
    folder1 = input("请输入第一个文件夹路径: ").strip()
    folder2 = input("请输入第二个文件夹路径: ").strip()
    folder3 = input("请输入第三个文件夹路径: ").strip()

    # 执行比较和剪切
    compare_and_move_files(folder1, folder2, folder3)
