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
  //camera parameters
  const double FX = 600.0;
  const double FY = 600.0;
  const double CX = 599.5;
  const double CY = 339.5;
  const double SCALE = 6553.5;

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
    
    if (!latest_depth_)

    

    //loop through every detection
    for(const auto & det : msg->detections)
    {
      //getting the center pixel of the boundin box
      double u = det.bbox.center.position.x;
      double v = det.bbox.center.position.y;

      //getting the center position of the depth
      int pixel_index = int(v)*latest_depth_->width + (int)u;

      //raw depth value from image data
      uint16_t raw_depth = ((uint16_t*)latest_depth_->data.data())[pixel_index];

      //convert into meters 
      double d = raw_depth / SCALE;

      //skip the invalid depth
      if(d <= 0.1 || d >= 8.0) continue;

      //projection to 3D
      double X = (u - CX) * d / FX;
      double Y = (v - CY) * d / FY;
      double Z = d;

      RCLCPP_INFO(this->get_logger(), "3D point: X=%.2f Y=%.2f Z=%.2f", X, Y, Z);

    }


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
};