#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>

class FusionNode : public rclcpp::Node
{ 
public:
  FusionNode(): Node("fusion_node")
  {
    RCLCPP_INFO(this->get_logger(), "Fusion node has started");
    depth_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
                "/camera/depth/image_raw", 
                10,
                std::bind(&FusionNode::depth_callback, this, std::placeholders::_1)
    );
    detection_sub_ = this->create_subscription<vision_msgs::msg::Detection2DArray>(
                "/yolo/detections",
                10,
                std::bind(&FusionNode::detection_callback, this, std::placeholders::_1)
    );
    RCLCPP_INFO(this->get_logger(), "Waiting for depth images....");
  }
//----------------------------------------------------------------------------------------------
private:
  void depth_callback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    latest_depth_ = msg;
    RCLCPP_INFO(this->get_logger(), "depth image recieved - wdith: %d height: %d",
                                    msg->width,
                                    msg->height);
  }
  //----------------------------------------------------------------------------------------------
  void detection_callback(const vision_msgs::msg::Detection2DArray::SharedPtr msg)
  {
    RCLCPP_INFO(this->get_logger(), "Detection recieved: %zu objects",
                                    msg->detections.size());
    
    if (latest_depth_ == 0)
    {
      RCLCPP_INFO(this->get_logger(), "No depth image recieved - skipping");
      return;
    }
  }
  //----------------------------------------------------------------------------------------------
  sensor_msgs::msg::Image::SharedPtr latest_depth_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_sub_;
  rclcpp::Subscription<vision_msgs::msg::Detection2DArray>::SharedPtr detection_sub_;
};

int main(int argc, char*argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FusionNode>());
  rclcpp::shutdown();

  return 0;
}