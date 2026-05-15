python3 infer_new_sensing.py \
    --root_data_path "your_stereo_data_folder_path" \
    --output_directory "your_output_folder_path" \
    --stereo_param_path "your_new_sensing_stereo_cam.yml" \
    --checkpoint "./checkpoint/igevrt8_s0.1.5.pth" \
    --resolution_mode "0" 


# resolution_mode "0: resize to 960x576, 1: center crop to 960x576", 2: full resolution