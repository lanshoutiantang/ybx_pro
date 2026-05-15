source setup.bash
# -l -r 修改为左右图文件夹的路径， -c为标定文件的json文件
# rosa run stereo_depth_estimation imaging_from_local -- -c=data/stereo_params.json -l=data/val_left.png -r=data/val_right.png
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/navigate/head/left/scene4_normal_rgb_000144_20260110_094422_344834.png -r=/mnt/testdata/2026_project_data/stereo/virtual/navigate/head/right/scene4_normal_rgb_000144_20260110_094422_344834.png  
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/carry/head/left/scene1_normal_near_rgb_000109.png -r=/mnt/testdata/2026_project_data/stereo/virtual/carry/head/right/scene1_normal_near_rgb_000109.png  
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/navigate/back/left/scene4_normal_rgb_000481_20260110_095622_961508.png -r=/mnt/testdata/2026_project_data/stereo/virtual/navigate/back/right/scene4_normal_rgb_000481_20260110_095622_961508.png  


# 石岩数据 2029张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/shiyan_0916/stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/shiyan_0916/left -r=/mnt/testdata/2026_project_data/stereo/shiyan_0916/right  
# 旧森云数据 5982张
echo "正在处理: 旧森云数据 carry 1982张"
# 旧森云数据 carry 1982张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/simulate_test_data/carry/sampled_dataset_banyun/left -r=/mnt/testdata/2026_project_data/stereo/simulate_test_data/carry/sampled_dataset_banyun/right  
echo "正在处理: 旧森云数据 navigate 2000张"
# # 旧森云数据 navigate 2000张
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate_1/left -r=/mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate_1/right  
# 导航concat图
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -i=/home/ubt/pr_test/pr_test_data/navigate
# 导航concat图拆分成left、right图
# rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -l=/home/ubt/pr_test/pr_navigate/left -r=/home/ubt/pr_test/pr_navigate/right  
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate_1/left -r=/mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate_1/right  



echo "正在处理: 旧森云数据 sps 2000张"
# 旧森云数据 sps 2000张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/simulate_test_data/1280_720_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left -r=/mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right  
# 新森云数据  51917张
echo "正在处理: 新森云数据  搬运carry场景：头部相机14711张"
# 新森云数据  搬运carry场景：头部相机14711张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/carry/head/left -r=/mnt/testdata/2026_project_data/stereo/virtual/carry/head/right  
echo "正在处理: 新森云数据  搬运carry场景：腰部相机14517张"
# 新森云数据  搬运carry场景：腰部相机14517张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/carry/waist/left -r=/mnt/testdata/2026_project_data/stereo/virtual/carry/waist/right  
echo "正在处理: 新森云数据  头部相机9169张（三一螺丝）"
# 新森云数据  头部相机9169张（三一螺丝）
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/sps/head/left -r=/mnt/testdata/2026_project_data/stereo/virtual/sps/head/right  
echo "正在处理: 新森云数据  导航场景：背部相机4431张"
# 新森云数据  导航场景：背部相机4431张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/navigate/back/left -r=/mnt/testdata/2026_project_data/stereo/virtual/navigate/back/right  
echo "正在处理: 新森云数据  导航场景：头部相机4718张"
# 新森云数据  导航场景：头部相机4718张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/navigate/head/left -r=/mnt/testdata/2026_project_data/stereo/virtual/navigate/head/right  
echo "正在处理: 新森云数据  导航场景：腰部相机4371张"
# 新森云数据  导航场景：腰部相机4371张
rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/virtual/1920_1536_stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/virtual/navigate/waist/left -r=/mnt/testdata/2026_project_data/stereo/virtual/navigate/waist/right  





# # 旧森云导航navigate数据汇总到一起
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/vnav_blur/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/vnav_normal/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/vnav_blur/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate/right
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/vnav_normal/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/navigate/sampled_dataset_navigate/right
# # 旧森云分拣sps数据汇总到一起
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_00_sampled_dataset/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_01_sampled_dataset/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_03_sampled_dataset/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_04_sampled_dataset/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sanyi_sampled_dataset/left/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/left



# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_00_sampled_dataset/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_01_sampled_dataset/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_03_sampled_dataset/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/liuqi_04_sampled_dataset/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right
# cp -r /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sanyi_sampled_dataset/right/*  /mnt/testdata/2026_project_data/stereo/simulate_test_data/sps/sampled_dataset_sps/right






















