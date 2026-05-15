# app_sps 双目深度推理脚本使用说明


在项目目录下使用 bash app_sps/infer_1920.sh 即可以生成深度、labels和深度相关指标

参数说明

```shell
# 默认使用ROI作为crop方式
resolution_mode=1 # 0: resize;  1: ROI
# 默认相机参数
stereo_param_path="${script_dir}/stereo_cam_1920.yml"
#双目模型版本
model_version="s0.1.9m"
# 双目路径
checkpoint_path="${script_dir}/../checkpoint/igevrt8_${model_version}.pth"

# ！！！重要 待处理数据home目录
BASE_DIR="/data/cv/visual_team2/vision_train_val/BaseModelData/seg/0.isaac_data/shiyan/train/shiyan_train_0210/"

# home目录下每个文件夹的名字，一次处理多个文件夹数据
DATA_FOLDERS=(
    "2026.2.10_train_normal_shiyan_alarm_sensor_disperse"
    "2026.2.10_train_normal_shiyan_fittings_N6_disperse"
)

# 子文件夹名字，一般为yolo或StereoCamRender，没有置空即可
SUBFOLDER_NAME="StereoCamRender"



    python3 ${script_dir}/../infer_new_sensing.py \
        --root_data_path "${data_path}" \
        --output_directory "${temp_result}" \
        --stereo_param_path "${stereo_param_path}" \
        --resolution_mode "${resolution_mode}" \
        --checkpoint "${checkpoint_path}" \
        --left_folder "images" \            # 左图文件夹名字，images or left，根据具体情况调整
        --num_gpus 8                        # gpu数量，一张卡写1就行，没有则为0

```

