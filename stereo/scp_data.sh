#!/bin/bash

# ==================== 配置区 ====================
# 源服务器路径前缀
SRC_BASE="/mnt/testdata/2026_project_data/stereo/virtual"

# 目标服务器配置
DEST_USER="ubt"
DEST_HOST="10.22.65.175"
DEST_BASE="/home/ubt/workspace/wenlei.yan/data/new_sensing_3_scenes"

# 需要传输的场景列表: (源子目录, 目标子目录)
declare -a SCENES=(
    "carry:carry"
    "navigate:nav"
    "sps:sps"
)

# 数据类型: head/depth
DATA_TYPE="head/depth"
# ================================================

echo "开始传输数据到 ${DEST_USER}@${DEST_HOST}"

for scene in "${SCENES[@]}"; do
    # 解析 源子目录:目标子目录
    src_sub="${scene%%:*}"
    dest_sub="${scene##*:}"

    src_path="${SRC_BASE}/${src_sub}/${DATA_TYPE}"
    dest_path="${DEST_BASE}/${dest_sub}"

    echo "传输: ${src_path} -> ${dest_path}"
    scp -r "${src_path}" "${DEST_USER}@${DEST_HOST}:${dest_path}"
done

echo "传输完成"
