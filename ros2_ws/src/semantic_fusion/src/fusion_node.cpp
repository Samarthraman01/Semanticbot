#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

class FusionNode : public rclcpp::Node
{ 
public:
  FusionNode(): Node("fusion_node")
  {
    RCLCPP_INFO(this->get_logger(), "Fusion node has started");
  }
private:

};

int main(int argc, char*argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FusionNode>());
  rclcpp::shutdown();

  return 0;
}