# Stereo Depth Inference

本项目提供了基于双目图像的深度估计脚本。

---

## 使用方法

### 双目3D成像
1. `infer_new_sensing.sh` 用于新森云的深度图生成，输入带畸变的左右图和标定文件
2. `infer_old_sensing.sh` 用于老森云的深度图生成，输入带畸变的左右图和标定文件
3. `batch_convert_depth_pointcloud_new_sensing.sh` 用于把新森云的深度图转换成点云，并上彩色
4. `batch_convert_depth_pointcloud_old_sensing.sh` 用于把老森云的深度图转换成点云，并上彩色


### 跑分拣应用指标
从nas拷贝数据后，部分文件夹需要重命名:
1. depth  -> gt
2. Images -> left

设置 `app_sps/infer_1920.sh` 里的 `# Settings`的要处理的数据路径DATA_FOLDERS、标定文件路径、模型路径、resolution_mode(是否使用ROI)。   

然后执行
```shell
bash infer_1920.sh 
```

运行结束后，关键结果会在 `result.txt` 文件里


`app_sps/yolo_vis.py`可以查看位姿是否正确

