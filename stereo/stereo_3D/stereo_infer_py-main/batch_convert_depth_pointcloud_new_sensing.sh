python3 batch_convert_depth_pointcloud_new_sensing.py \
    --root_dir "your_data_folder_path" \
    --stereo_param_path "your_new_sensing_stereo_cam.yml" \
    --interval "1" \
    --resolution_mode "0" \
    --clear_edges

# resolution_mode "0: resize to 960x576, 1: center crop to 960x576", 2: full resolution
