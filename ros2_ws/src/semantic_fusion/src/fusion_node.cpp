#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

class FusionNode : public rclcpp::Node
{ 
public:
  FusionNode(): Node("fusion_node")
  {
    RCLCPP_INFO(this->get_logger(), "Fusion node has started");
    depth_sub = this->create_subscription<sensor_msgs::msg::Image>(
                "/camera/depth/image_raw", 
                10,
                std::bind(&FusionNode::depth_callback, this, std::placeholders::_1)
    );
    RCLCPP_INFO(this->get_logger(), "Waiting for depth images....");
  }
private:
  void depth_callback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    RCLCPP_INFO(this->get_logger(), "depth image recieved - wdith: %d height: %d",
                                    msg->width,
                                    msg->height);
  }
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_sub;
};

int main(int argc, char*argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FusionNode>());
  rclcpp::shutdown();

  return 0;
}