
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Settings
resolution_mode=1 # 0: resize;  1: ROI
stereo_param_path="${script_dir}/stereo_cam_1920.yml"
model_version="s0.1.9m"
checkpoint_path="${script_dir}/../checkpoint/igevrt8_${model_version}.pth"
BASE_DIR="/data/cv/visual_team2/vision_train_val/BaseModelData/seg/0.isaac_data/shiyan/train/shiyan_train_0210/"

DATA_FOLDERS=(
    "2026.2.10_train_normal_shiyan_alarm_sensor_disperse"
    "2026.2.10_train_normal_shiyan_fittings_N6_disperse"
)

SUBFOLDER_NAME="StereoCamRender"


for data_path in "${DATA_FOLDERS[@]}"; do
    data_path=${BASE_DIR}/${data_path}/$SUBFOLDER_NAME
    echo ""
    echo "Processing folder: ${data_path}"
    echo ""
    temp_result="${data_path}/results_${model_version}_${resolution_mode}"
    # remove ${temp_result} and mkdir
    if [ -d "${temp_result}" ]; then
        rm -rf "${temp_result}"
    fi
    mkdir -p "${temp_result}"


    # Generate stereo depth and rgb
    python3 ${script_dir}/../infer_new_sensing.py \
        --root_data_path "${data_path}" \
        --output_directory "${temp_result}" \
        --stereo_param_path "${stereo_param_path}" \
        --resolution_mode "${resolution_mode}" \
        --checkpoint "${checkpoint_path}" \
        --left_folder "images" \
        --num_gpus 8

    # Generate labels
    python3 ${script_dir}/convert_labels_1920.py \
            --src_labels ${data_path}/labels \
            --dst_labels ${temp_result}/labels_960 \
            --resolution_mode ${resolution_mode}

    # Stat accuracy
    python3 ${script_dir}/check_stereo_depth_acc.py \
            --data_root ${temp_result} \
            --stereo_depth ${temp_result}/depth \
            --sim_depth ${data_path}/depth \
            --labels labels_960 \
            --occlusion ${data_path}/occlusion \
            --images ${temp_result}/rgb \
            --poses ${data_path}/poses \
            --badcase_dir bad_cases_960 \
            --abs_thresh 0.01 \
            --resolution_mode ${resolution_mode} \
            --depth_acc ${temp_result}/depth_acc

done