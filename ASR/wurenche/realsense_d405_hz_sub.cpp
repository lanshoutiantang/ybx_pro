#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include <fstream>
#include <sstream>
#include<thread>

/**
 *  ""/sensor/camera/realsense_d405/image/raw"": 24.9,
    ""/sensor/camera/fisheye_right/image/raw"": 25.0,
    ""/sensor/camera/head_back_rgbd/color/raw"": 30.1,
    ""/sensor/camera/head_front_rgbd/color/raw"": 29.4,
    ""/sensor/camera/stereo_left/image/raw"": 25.1,
    ""/sensor/camera/stereo_right/image/raw"": 25.1,
    ""/sensor/camera/waist_back_rgbd/color/raw"": 30.2,
    ""/sensor/camera/waist_front_rgbd/color/raw"": 30.1,
    ""/sensor/Imu/orin"": 200.4
*/

class SensorHzSub : public rclcpp::Node
{
public:
  SensorHzSub() : Node("realsense_d405_hz")
  {
    file_realsense_d405_time_.open(realsense_d405_file_time_,  std::ios::app);
    file_realsense_d405_hz_.open(realsense_d405_file_hz_,  std::ios::app);


    openFile(file_realsense_d405_time_);
    openFile(file_realsense_d405_hz_);



    run_th_ = std::thread(&SensorHzSub::run, this);

    auto qos = rclcpp::QoS(rclcpp::KeepLast(10));
    qos.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);           // RMW_QOS_POLICY_RELIABILITY_RELIABLE 或 RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT
    qos.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);      // RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL 或 RMW_QOS_POLICY_DURABILITY_VOLATILE

    // 创建订阅者
    realsense_d405_sub_ = this->create_subscription<sensor_msgs::msg::Image>("/camera/camera/color/image_rect_raw", qos,
        std::bind(&SensorHzSub::cb1, this, std::placeholders::_1));

  }

  void cb1(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    // std::cout << "cb1" << std::endl;
    if (realsense_d405_first_in_)
    {
      realsense_d405_start_time_ = std::chrono::steady_clock::now();
      realsense_d405_last_time_ = std::chrono::steady_clock::now();
      realsense_d405_first_in_ = false;
      std::lock_guard<std::mutex> lock(queue_mutex_);
      realsense_d405_last_string_time_ = getCurrentTime();
    }

    realsense_d405_now_time_ = std::chrono::steady_clock::now();
    {
      std::lock_guard<std::mutex> lock(queue_mutex_);
      realsense_d405_now_string_time_ = getCurrentTime();
    }
    auto duration1 = std::chrono::duration_cast<std::chrono::seconds>(realsense_d405_now_time_ - realsense_d405_start_time_);
    auto duration2 = std::chrono::duration_cast<std::chrono::milliseconds>(realsense_d405_now_time_ - realsense_d405_last_time_);


    if (file_realsense_d405_time_.is_open()) {
      if(duration2.count() > 1000){
        file_realsense_d405_time_ << realsense_d405_last_string_time_ << "," << realsense_d405_now_string_time_ << "," << std::to_string(duration2.count()) << ","  << "1" << "\n";
      }else if(duration2.count() > 500){
        file_realsense_d405_time_ << realsense_d405_last_string_time_ << "," << realsense_d405_now_string_time_ << "," << std::to_string(duration2.count()) << ","  << "0.5" << "\n";
      }else if(duration2.count() > 100){
        file_realsense_d405_time_ << realsense_d405_last_string_time_ << "," << realsense_d405_now_string_time_ << "," << std::to_string(duration2.count()) << ","  << "0.1" << "\n";
      }else{
        //str = str+"\n"
      }
    } else {
      std::cerr << "File file_realsense_d405_time_ is not open!" << std::endl;
    }
    
    // 记录频率
    // 取1s的回调次数用于计算频率
    if (duration1.count() < 1)
    {
      realsense_d405_cnt_++;
      std::lock_guard<std::mutex> lock(queue_mutex_);
      realsense_d405_string_time_ = getCurrentTime();
    }
    else
    {
      if (file_realsense_d405_hz_.is_open()) {
        std::lock_guard<std::mutex> lock(realsense_d405_mutex_);
        file_realsense_d405_hz_ << realsense_d405_string_time_ << "," << realsense_d405_cnt_ << "\n";
      } else {
        std::cerr << "File file_realsense_d405_hz_ is not open!" << std::endl;
      }
      RCLCPP_INFO(this->get_logger(), "当前 realsense_d405 的频率为: '%d'", realsense_d405_cnt_);
      realsense_d405_cnt_ = 0;
      realsense_d405_start_time_ = std::chrono::steady_clock::now();
      // ULOGI_S() << "当前servo_cmd的频率为: " << realsense_d405_cnt_; // 输出收到的消息内容
    }

    realsense_d405_last_time_ = realsense_d405_now_time_;
    realsense_d405_last_string_time_ = realsense_d405_now_string_time_;
    
  }

  
  std::string getCurrentTime() {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    auto now_us = std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()) % 1000000;

    std::tm* now_tm_ptr = std::localtime(&now_time_t);  // 使用本地时间
    if (now_tm_ptr == nullptr) {
        throw std::runtime_error("Failed to get local time");
    }
    std::tm now_tm = *now_tm_ptr;

    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%d_%H:%M:%S");
    oss << '.' << std::setfill('0') << std::setw(6) << now_us.count();

    return oss.str();
}

  void openFile(std::ofstream &file){
    if (!file.is_open()) {
      std::cerr << "File could not be opened for writing!\n";
    }
  }

  void closeFile(std::ofstream &file){
    if (file.is_open()) {
        file.close();
    }
  }

  void run(){
    rclcpp::Rate rate(50);
    while(rclcpp::ok()){
      auto now = std::chrono::steady_clock::now();
      auto duration_realsense_d405 = std::chrono::duration_cast<std::chrono::seconds>(now - realsense_d405_now_time_);


      // 左鱼眼掉线超时1s监控
      if(duration_realsense_d405.count() > 1){
        std::string now_time = "";
        {
          std::lock_guard<std::mutex> lock(queue_mutex_);
          now_time = getCurrentTime();
        }
        
        std::lock_guard<std::mutex> lock(realsense_d405_mutex_);
        file_realsense_d405_hz_ << now_time << "," << "0.0" << "\n";
        realsense_d405_now_time_ = now;
      }

     

      
      rate.sleep();
    }
  }


  ~SensorHzSub(){
    closeFile(file_realsense_d405_time_);
    closeFile(file_realsense_d405_hz_);
  }


private:
    std::thread run_th_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr realsense_d405_sub_;


    std::ofstream file_realsense_d405_time_, file_realsense_d405_hz_;


    std::string realsense_d405_file_time_ = "/home/ubt/workspace/jzd_test/realsense_d405_time.txt";
    std::string realsense_d405_file_hz_ = "/home/ubt/workspace/jzd_test/realsense_d405_hz.csv";



    std::atomic_bool realsense_d405_first_in_ = true;


    int realsense_d405_cnt_ = 0;


    std::string realsense_d405_string_time_ = "0.0";
    std::string realsense_d405_last_string_time_ = "0.0";
    std::string realsense_d405_now_string_time_ = "0.0";



    std::chrono::steady_clock::time_point realsense_d405_start_time_;
    std::chrono::steady_clock::time_point realsense_d405_last_time_;
    std::chrono::steady_clock::time_point realsense_d405_now_time_;


    std::mutex queue_mutex_;
    std::mutex realsense_d405_mutex_;

};






int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SensorHzSub>());
  rclcpp::shutdown();

  return 0;
}