/*
 * SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

#include <cuda_runtime.h>
#include <string.h>
#include <dlfcn.h>
#include <vector>
#include <dlfcn.h>
#include <iostream>
#include <fstream>
#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include <stb_image_write.h>

#include "bevfusion/bevfusion.hpp"
#include "common/check.hpp"
#include "common/tensor.hpp"
#include "common/timer.hpp"
#include "common/visualize.hpp"

#include <opencv2/opencv.hpp>
#include <sys/time.h>
#include <cuda_fp16.h>

#include <cstdint>
#include <filesystem>

static std::vector<unsigned char *> load_images(std::vector<std::string> imgs)
{
  std::vector<unsigned char *> images;
  for (int i = 0; i < imgs.size(); ++i)
  {
    int width, height, channels;
    images.push_back(stbi_load(imgs[i].c_str(), &width, &height, &channels, 0));
    // std::cout << "imgs[i].c_str(): " << imgs[i].c_str() << std::endl;
    // printf("Image info[%d]: %d x %d : %d\n", i, width, height, channels);
  }
  return images;
}

static void free_images(std::vector<unsigned char *> &images)
{
  for (size_t i = 0; i < images.size(); ++i)
    stbi_image_free(images[i]);

  images.clear();
}

static void visualize(const std::vector<bevfusion::head::transbbox::BoundingBox> &bboxes, const nv::Tensor &lidar_points,
                      const std::vector<unsigned char *> images, const nv::Tensor &lidar2image, const std::string &save_path,
                      cudaStream_t stream)
{
  std::vector<nv::Prediction> predictions(bboxes.size());
  memcpy(predictions.data(), bboxes.data(), bboxes.size() * sizeof(nv::Prediction));

  int padding = 300;
  int lidar_size = 1024;
  int content_width = lidar_size + padding * 3;
  int content_height = 1080;
  nv::SceneArtistParameter scene_artist_param;
  scene_artist_param.width = content_width;
  scene_artist_param.height = content_height;
  scene_artist_param.stride = scene_artist_param.width * 3;

  nv::Tensor scene_device_image(std::vector<int>{scene_artist_param.height, scene_artist_param.width, 3}, nv::DataType::UInt8);
  scene_device_image.memset(0x00, stream);

  scene_artist_param.image_device = scene_device_image.ptr<unsigned char>();
  auto scene = nv::create_scene_artist(scene_artist_param);

  nv::BEVArtistParameter bev_artist_param;
  bev_artist_param.image_width = content_width;
  bev_artist_param.image_height = content_height;
  bev_artist_param.rotate_x = 70.0f;
  bev_artist_param.norm_size = lidar_size * 0.5f;
  bev_artist_param.cx = content_width * 0.5f;
  bev_artist_param.cy = content_height * 0.5f;
  bev_artist_param.image_stride = scene_artist_param.stride;

  auto points = lidar_points.to_device();
  auto bev_visualizer = nv::create_bev_artist(bev_artist_param);
  bev_visualizer->draw_lidar_points(points.ptr<nvtype::half>(), points.size(0));
  bev_visualizer->draw_prediction(predictions, false);
  bev_visualizer->draw_ego();
  bev_visualizer->apply(scene_device_image.ptr<unsigned char>(), stream);

  nv::ImageArtistParameter image_artist_param;
  image_artist_param.num_camera = images.size();
  image_artist_param.image_width = 1280;
  image_artist_param.image_height = 720;
  image_artist_param.image_stride = image_artist_param.image_width * 3;
  image_artist_param.viewport_nx4x4.resize(images.size() * 4 * 4);
  memcpy(image_artist_param.viewport_nx4x4.data(), lidar2image.ptr<float>(),
         sizeof(float) * image_artist_param.viewport_nx4x4.size());

  int gap = 0;
  int camera_width = 500;
  int camera_height = static_cast<float>(camera_width / (float)image_artist_param.image_width * image_artist_param.image_height);
  int offset_cameras[][3] = {
      {-camera_width / 2, -content_height / 2 + gap, 0},
      {content_width / 2 - camera_width - gap, -content_height / 2 + camera_height / 2, 0},
      {-content_width / 2 + gap, -content_height / 2 + camera_height / 2, 0},
      {-camera_width / 2, +content_height / 2 - camera_height - gap, 1},
      {-content_width / 2 + gap, +content_height / 2 - camera_height - camera_height / 2, 0},
      {content_width / 2 - camera_width - gap, +content_height / 2 - camera_height - camera_height / 2, 1}};

  auto visualizer = nv::create_image_artist(image_artist_param);
  for (size_t icamera = 0; icamera < images.size(); ++icamera)
  {
    int ox = offset_cameras[icamera][0] + content_width / 2;
    int oy = offset_cameras[icamera][1] + content_height / 2;
    bool xflip = static_cast<bool>(offset_cameras[icamera][2]);
    visualizer->draw_prediction(icamera, predictions, xflip);

    nv::Tensor device_image(std::vector<int>{720, 1280, 3}, nv::DataType::UInt8);
    device_image.copy_from_host(images[icamera], stream);

    if (xflip)
    {
      auto clone = device_image.clone(stream);
      scene->flipx(clone.ptr<unsigned char>(), clone.size(1), clone.size(1) * 3, clone.size(0), device_image.ptr<unsigned char>(),
                   device_image.size(1) * 3, stream);
      checkRuntime(cudaStreamSynchronize(stream));
    }
    visualizer->apply(device_image.ptr<unsigned char>(), stream);

    scene->resize_to(device_image.ptr<unsigned char>(), ox, oy, ox + camera_width, oy + camera_height, device_image.size(1),
                     device_image.size(1) * 3, device_image.size(0), 0.8f, stream);
    checkRuntime(cudaStreamSynchronize(stream));
  }

  printf("Save to %s\n", save_path.c_str());
  stbi_write_jpg(save_path.c_str(), scene_device_image.size(1), scene_device_image.size(0), 3,
                 scene_device_image.to_host(stream).ptr(), 100);
}

std::shared_ptr<bevfusion::Core> create_core(const std::string &model, const std::string &precision, const int lidar_dim)
{
  printf("Create by %s, %s\n", model.c_str(), precision.c_str());
  bevfusion::camera::NormalizationParameter normalization;
  normalization.image_width = 1280;
  normalization.image_height = 720;
  normalization.output_width = 704;
  normalization.output_height = 256;
  normalization.num_camera = 5;
  normalization.resize_lim = 0.6f;
  normalization.interpolation = bevfusion::camera::Interpolation::Bilinear;

  float mean[3] = {0.485, 0.456, 0.406};
  float std[3] = {0.229, 0.224, 0.225};
  normalization.method = bevfusion::camera::NormMethod::mean_std(mean, std, 1 / 255.0f, 0.0f);

  bevfusion::lidar::VoxelizationParameter voxelization;
  voxelization.min_range = nvtype::Float3(-54.0f, -54.0f, -5.0);
  voxelization.max_range = nvtype::Float3(+54.0f, +54.0f, +3.0);
  voxelization.voxel_size = nvtype::Float3(0.075f, 0.075f, 0.2f);
  voxelization.grid_size =
      voxelization.compute_grid_size(voxelization.max_range, voxelization.min_range, voxelization.voxel_size);
  voxelization.max_points_per_voxel = 10;
  voxelization.max_points = 300000;
  voxelization.max_voxels = 160000;
  voxelization.num_feature = lidar_dim;

  bevfusion::lidar::SCNParameter scn;
  scn.voxelization = voxelization;
  scn.model = nv::format("model/%s/lidar.backbone.xyz.onnx", model.c_str());
  scn.order = bevfusion::lidar::CoordinateOrder::XYZ;

  if (precision == "int8")
  {
    scn.precision = bevfusion::lidar::Precision::Int8;
  }
  else
  {
    scn.precision = bevfusion::lidar::Precision::Float16;
  }

  bevfusion::camera::GeometryParameter geometry;
  geometry.xbound = nvtype::Float3(-54.0f, 54.0f, 0.3f);
  geometry.ybound = nvtype::Float3(-54.0f, 54.0f, 0.3f);
  geometry.zbound = nvtype::Float3(-10.0f, 10.0f, 20.0f);
  geometry.dbound = nvtype::Float3(1.0, 60.0f, 0.5f);
  geometry.image_width = 704;
  geometry.image_height = 256;
  geometry.feat_width = 88;
  geometry.feat_height = 32;
  geometry.num_camera = 5;
  geometry.geometry_dim = nvtype::Int3(360, 360, 80);

  bevfusion::head::transbbox::TransBBoxParameter transbbox;
  transbbox.out_size_factor = 8;
  transbbox.pc_range = {-54.0f, -54.0f};
  transbbox.post_center_range_start = {-61.2, -61.2, -10.0};
  transbbox.post_center_range_end = {61.2, 61.2, 10.0};
  transbbox.voxel_size = {0.075, 0.075};
  transbbox.model = nv::format("model/%s/build/head.bbox.plan", model.c_str());
  transbbox.confidence_threshold = 0.13f;
  transbbox.sorted_bboxes = true;

  bevfusion::CoreParameter param;
  param.camera_model = nv::format("model/%s/build/camera.backbone.plan", model.c_str());
  param.normalize = normalization;
  param.lidar_scn = scn;
  param.geometry = geometry;
  param.transfusion = nv::format("model/%s/build/fuser.plan", model.c_str());
  param.transbbox = transbbox;
  param.camera_vtransform = nv::format("model/%s/build/camera.vtransform.plan", model.c_str());
  return bevfusion::create_core(param);
}

typedef unsigned short self_half;
static inline self_half __internal_float2half(const float f)
{
  unsigned int x;
  unsigned int u;
  unsigned int result;
  unsigned int sign;
  unsigned int remainder;
  (void)memcpy(&x, &f, sizeof(f));
  u = (x & 0x7fffffffU);
  sign = ((x >> 16U) & 0x8000U);
  // NaN/+Inf/-Inf
  if (u >= 0x7f800000U)
  {
    remainder = 0U;
    result = ((u == 0x7f800000U) ? (sign | 0x7c00U) : 0x7fffU);
  }
  else if (u > 0x477fefffU)
  { // Overflows
    remainder = 0x80000000U;
    result = (sign | 0x7bffU);
  }
  else if (u >= 0x38800000U)
  { // Normal numbers
    remainder = u << 19U;
    u -= 0x38000000U;
    result = (sign | (u >> 13U));
  }
  else if (u < 0x33000001U)
  { // +0/-0
    remainder = u;
    result = sign;
  }
  else
  { // Denormal numbers
    const unsigned int exponent = u >> 23U;
    const unsigned int shift = 0x7eU - exponent;
    unsigned int mantissa = (u & 0x7fffffU);
    mantissa |= 0x800000U;
    remainder = mantissa << (32U - shift);
    result = (sign | (mantissa >> shift));
    result &= 0x0000FFFFU;
  }

  unsigned short x_tmp = static_cast<unsigned short>(result);
  if ((remainder > 0x80000000U) ||
      ((remainder == 0x80000000U) && ((x & 0x1U) != 0U)))
  {
    x_tmp++;
  }
  return x_tmp;
}

void nms_sorted_bboxes(std::vector<bevfusion::head::transbbox::BoundingBox> &bboxes,
                       std::vector<float> dist_threshold)
{
  std::vector<int> picked;
  std::set<int> picked_id;
  picked.clear();
  picked_id.clear();
  const int n = bboxes.size();
  std::vector<bevfusion::head::transbbox::BoundingBox> nms_bboxes;

  for (int i = 0; i < n; i++)
  {
    const bevfusion::head::transbbox::BoundingBox &a = bboxes[i];

    int keep = 1;
    for (int j = 0; j < (int)picked.size(); j++)
    {
      const bevfusion::head::transbbox::BoundingBox &b = bboxes[picked[j]];
      if (picked_id.count(a.id + 1) > 0 && a.id == b.id)
      {
        double distance = std::sqrt((a.position.x - b.position.x) * (a.position.x - b.position.x) +
                                    (a.position.y - b.position.y) * (a.position.y - b.position.y));
        // std::cout << class_names_[a.id] << " Distance:" << distance << std::endl;
        if (distance < dist_threshold[a.id])
          keep = 0;
      }
    }

    if (keep)
    {
      picked.push_back(i);
      picked_id.insert(a.id + 1);
      nms_bboxes.push_back(bboxes[i]);
    }
  }
  if (nms_bboxes.size() > 0)
  {
    bboxes.clear();
    bboxes = nms_bboxes;
  }
}

int main(int argc, char **argv)
{

  const char *data = "changsha_00000";
  const char *model = "onnx_fp16_20240829";
  const char *precision = "fp16";
  const int lidar_dim = 5; //!!!Note the dimensions of the incoming point cloud

  std::list<std::string> myList = {"2023-09-08/", "2023-10-07/", "2023-11-10/", "2023-11-13/", "2023-11-16/", "2024-02-29/","2024-04-10_car-0_hz0.5/", "2024-05-13_bicycle_hz1/", "2024-05-13_truck_hz0.5/"};

  for (const std::string& str : myList) {
      /*********************************************/
      std::string root_path = "./";
      std::string test_data = str;
      /*********************************************/

      std::string result_folder_path = root_path + test_data + "/predict/";

      if (argc > 1)
        data = argv[1];
      if (argc > 2)
        model = argv[2];
      if (argc > 3)
        precision = argv[3];
      dlopen("libcustom_layernorm.so", RTLD_NOW);

      auto core = create_core(model, precision, lidar_dim);
      if (core == nullptr)
      {
        printf("Core has been failed.\n");
        return -1;
      }

      cudaStream_t stream;
      cudaStreamCreate(&stream);

      core->print();
      core->set_timer(false);

      // Load matrix to host
      auto camera2lidar = nv::Tensor::load("./model/camera2lidar.tensor", false);
      auto camera_intrinsics = nv::Tensor::load("./model/camera_intrinsics.tensor", false);
      auto lidar2image = nv::Tensor::load("./model/lidar2image.tensor", false);
      auto img_aug_matrix = nv::Tensor::load("./model/img_aug_matrix.tensor", false);
      core->update(camera2lidar.ptr<float>(), camera_intrinsics.ptr<float>(), lidar2image.ptr<float>(), img_aug_matrix.ptr<float>(),
                   stream);
      // core->free_excess_memory();

      std::string CAM0_dir = root_path + test_data + "/camera/CAM0";
      std::string CAM4_dir = root_path + test_data + "/camera/CAM4";
      std::string CAM5_dir = root_path + test_data + "/camera/CAM5";
      std::string CAM6_dir = root_path + test_data + "/camera/CAM6";
      std::string CAM7_dir = root_path + test_data + "/camera/CAM7";

      std::string Lidar_dir = root_path + test_data + "/bin5";
      std::string Label_dir = root_path + test_data + "/label";

      std::cout << "Lidar_dir: " << Lidar_dir << std::endl;

      std::vector<cv::String> label_list;
      cv::glob(Lidar_dir, label_list);
      std::cout << "label_list.size(): " << label_list.size() << std::endl;
      for (int i = 0; i < label_list.size(); i++)
      {
        std::string label_path = label_list[i];
        std::cout << "i: " << i << " label_path: " << label_path << std::endl;

        int pos = label_path.find_last_of('/');
        std::string label_name(label_path.substr(pos + 1));
        std::string timestamp = label_name.substr(0, label_name.length()-4);

        std::string img0_path = CAM0_dir + "/" + timestamp + ".jpg";
        std::string img4_path = CAM4_dir + "/" + timestamp + ".jpg";
        std::string img5_path = CAM5_dir + "/" + timestamp + ".jpg";
        std::string img6_path = CAM6_dir + "/" + timestamp + ".jpg";
        std::string img7_path = CAM7_dir + "/" + timestamp + ".jpg";

        std::vector<std::string> imgs{img0_path, img4_path, img5_path, img6_path, img7_path};
        auto images = load_images(imgs);

        std::string lidar_path = Lidar_dir + "/" + timestamp + ".bin"; //!!!确保输入的原始点云文件是5维的
        std::ifstream file(lidar_path, std::ios::binary);
        if (!file.is_open())
        {
          std::cerr << "Failed to open file " << lidar_path << std::endl;
          return -1;
        }
        std::vector<bevfusion::Point> vec_points;
        while (!file.eof())
        {
          bevfusion::Point point;
          file.read(reinterpret_cast<char *>(&point), sizeof(bevfusion::Point));
          if (file.eof())
            break;
          // std::cout << "X: " << point.x << ", Y: " << point.y << ", Z: " << point.z << std::endl;
          if (point.x < -54.0 || point.x > 54.0)
            continue;
          if (point.y < -54.0 || point.y > 54.0)
            continue;
          if (point.z < -5 || point.z > 3)
            continue;
          vec_points.push_back(point);
        }
        file.close();

        self_half *points = new self_half[vec_points.size() * lidar_dim];

        for (int i = 0; i < vec_points.size(); i++)
        {
          points[i * lidar_dim + 0] = __internal_float2half(vec_points[i].x);
          points[i * lidar_dim + 1] = __internal_float2half(vec_points[i].y);
          points[i * lidar_dim + 2] = __internal_float2half(vec_points[i].z);
          points[i * lidar_dim + 3] = __internal_float2half(vec_points[i].i);
          points[i * lidar_dim + 4] = __internal_float2half(vec_points[i].t);
        }


        std::vector<int32_t> shape{vec_points.size(), lidar_dim};
        nv::Tensor lidar_points = nv::Tensor::from_data_reference(
            points, shape, nv::DataType::Float16, false);

        // std::cout << "lidar_points.shape.size(): " << lidar_points.shape.size() << std::endl;
        // std::cout << "lidar_points[0]: " << lidar_points.shape[0] << std::endl;
        // std::cout << "lidar_points[1]: " << lidar_points.shape[1] << std::endl;

        // //打印点云中的值
        // auto ptr = lidar_points.ptr<nvtype::half>();
        // auto lidar_shape = lidar_points.shape;
        // for(int w=0; w < 3; w ++ ){ //lidar_points.shape[0]
        //   for(int h=0; h <lidar_points.shape[1]; h ++ ){
        //     __half half_value; // 创建一个 __half 类型的变量
        //     memcpy(&half_value, &ptr[h].__x, sizeof(unsigned short)); // 将 unsigned short 的值复制到 __half 变量中
        //     // memcpy(&half_value, &ptr[w*lidar_points.shape[0]+h].__x, sizeof(unsigned short)); // 将 unsigned short 的值复制到 __half 变量中
        //     float float_value = __half2float(half_value); // 转换 __half 到 float
        //     std::cout << "w: " << w << " h: " << h << " lidar_points: " << float_value << std::endl; // 打印 float 值
        //   }
        // }

        struct timeval time_start, time_end;
        gettimeofday(&time_start, NULL);
        auto bboxes = core->forward((const unsigned char **)images.data(), lidar_points.ptr<nvtype::half>(), lidar_points.size(0), stream);

        // convert the Center from Bottem to Geometric_Center
        for (int i = 0; i < bboxes.size(); i++)
        {
          float GeometricCenter_z = bboxes[i].position.z + bboxes[i].size.h / 2;
          bboxes[i].position.z = GeometricCenter_z;
        }

        std::vector<float> DISTANCE_THRESHOLD{0.2, 0.2, 0.7, 1, 2.5, 1, 1, 0.2, 0.5, 1, 0.2, 1, 1}; // "pedestrian", "bicycle", "car", "bus", "truck", "forklift", "trailer", "rack", "shelves", "traffic_cone", "goods", "traffic_light", "other_vehicle";
        if (bboxes.size() > 0)
        {
          std::sort(
              bboxes.begin(), bboxes.end(),
              [](const bevfusion::head::transbbox::BoundingBox &a,
                 const bevfusion::head::transbbox::BoundingBox &b)
              { return a.score > b.score && a.id == b.id; });
          nms_sorted_bboxes(bboxes, DISTANCE_THRESHOLD);
        }
        gettimeofday(&time_end, NULL);
        auto usedTime = (time_end.tv_sec - time_start.tv_sec) * 1000.0 + (time_end.tv_usec - time_start.tv_usec) / 1000.0;
        std::cout << "cost: " << usedTime << "ms" << std::endl;

        std::string result_file = result_folder_path + timestamp + ".txt";
        std::ofstream det_result(result_file);
        for (auto box : bboxes)
        {
          // std::vector<bevfusion::Point> bev_points = transformation_predictions(box);
          // det_result<<bboxes[i].position.x<<" "<<bboxes[i].position.y<<" "<<bboxes[i].position.z<<" "<<bboxes[i].size.w<<" "<<bboxes[i].size.l<<" "<<bboxes[i].size.h<<" "<<bboxes[i].z_rotation<<" "<<bboxes[i].velocity.vx<<" "<<bboxes[i].velocity.vy<<" "<<bboxes[i].id<<" "<<bboxes[i].score<<std::endl;
          // det_result << box.id << " " << box.position.x << " " << box.position.y << " " << box.position.z << " " << box.size.w << " " << box.size.l << " " << box.size.h << " " << box.z_rotation << " " << box.score << std::endl;
          det_result << box.id << " " << box.position.x << " " << box.position.y << " " << box.position.z << " " << box.size.l << " " << box.size.w << " " << box.size.h << " " << -(box.z_rotation + M_PI / 2) << " " << box.score << std::endl;
        }
        // visualize and save to jpg
        // visualize(bboxes, lidar_points, images, lidar2image, "build/cuda-bevfusion.jpg", stream);

        // destroy memory
        free_images(images);
      }
      checkRuntime(cudaStreamDestroy(stream));
  }

  return 0;
}