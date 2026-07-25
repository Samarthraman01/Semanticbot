#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>
#include <vector>
#include <fstream>
#include <array>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>

class FusionNode : public rclcpp::Node
{ 
public:
  FusionNode() : Node("fusion_node")
  {
    RCLCPP_INFO(this->get_logger(), "Fusion node has started");

    depth_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
      "/camera/depth/image_raw", 10,
      std::bind(&FusionNode::depth_callback, this, std::placeholders::_1)
    );

    detection_sub_ = this->create_subscription<vision_msgs::msg::Detection2DArray>(
      "/yolo/detections", 10,
      std::bind(&FusionNode::detection_callback, this, std::placeholders::_1)
    );

    cloud_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/semantic/pointcloud", 10);

    RCLCPP_INFO(this->get_logger(), "Waiting for depth images...");
    load_poses("/workspace/data/Replica/office0/traj.txt");
  }


private:
  // Camera parameters
  const double FX_    = 600.0;
  const double FY_    = 600.0;
  const double CX_    = 599.5;
  const double CY_    = 339.5;
  const double SCALE_ = 6553.5;

  //for camera poses 
  std::vector<std::vector<double>> poses_;
  int current_frame_ = 0;

  std::vector<std::array<double, 3>> world_points_;

  // Depth callback — stores latest depth image
  void depth_callback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    latest_depth_ = msg;
    RCLCPP_INFO(this->get_logger(),
      "Depth image received — width: %d height: %d",
      msg->width, msg->height);
  }

  // Detection callback — fuses detections with depth
  void detection_callback(const vision_msgs::msg::Detection2DArray::SharedPtr msg)
  {
    RCLCPP_INFO(this->get_logger(),
      "Detections received: %zu objects",
      msg->detections.size());

    // check depth is ready
    if(!latest_depth_)
    {
      RCLCPP_WARN(this->get_logger(), "No depth image yet — skipping");
      return;
    }

    // loop through every detection
    for(const auto & det : msg->detections)
    {
      // get centre pixel of bounding box
      double u = det.bbox.center.position.x;
      double v = det.bbox.center.position.y;

      // get depth at centre pixel
      int pixel_index = (int)v * latest_depth_->width + (int)u;
      uint16_t raw_depth = ((uint16_t*)latest_depth_->data.data())[pixel_index];

      // convert to metres
      double d = raw_depth / SCALE_;

      // skip invalid depth
      if(d <= 0.1 || d > 8.0) continue;

      // project to 3D camera space
      double X = (u - CX_) * d / FX_;
      double Y = (v - CY_) * d / FY_;
      double Z = d;

      // transform to world space using pose
      if(current_frame_ < (int)poses_.size())
      {
        const auto & pose = poses_[current_frame_];

        double Xw = pose[0]*X + pose[1]*Y + pose[2]*Z  + pose[3];
        double Yw = pose[4]*X + pose[5]*Y + pose[6]*Z  + pose[7];
        double Zw = pose[8]*X + pose[9]*Y + pose[10]*Z + pose[11];

        // store world point for publishing
        world_points_.push_back({Xw, Yw, Zw});
      }
    }

    current_frame_++;
    publish_cloud();
  }

  // Load camera poses from traj.txt
  void load_poses(const std::string & path)
  {
    std::ifstream file(path);
    if(!file.is_open())
    {
      RCLCPP_ERROR(this->get_logger(),
        "Cannot open file: %s", path.c_str());
      return;
    }

    std::vector<double> row_vals;
    double val;
    int count = 0;

    while(file >> val)
    {
      row_vals.push_back(val);
      count++;

      if(count == 16)
      {
        poses_.push_back(row_vals);
        row_vals.clear();
        count = 0;
      }
    }

    RCLCPP_INFO(this->get_logger(),
      "Loaded %zu poses", poses_.size());
  }

  void publish_cloud()
  {
    if(world_points_.empty()) return;

    sensor_msgs::msg::PointCloud2 cloud_msg;
    cloud_msg.header.stamp = this->now();
    cloud_msg.header.frame_id = "map";
    cloud_msg.height = 1;
    cloud_msg.width = world_points_.size();
    cloud_msg.is_dense = false;

    sensor_msgs::PointCloud2Modifier modifier(cloud_msg);
    modifier.setPointCloud2FieldsByString(2, "xyz", "rgb");
    modifier.resize(world_points_.size());

    sensor_msgs::PointCloud2Iterator<float> iter_x(cloud_msg, "x");
    sensor_msgs::PointCloud2Iterator<float> iter_y(cloud_msg, "y");
    sensor_msgs::PointCloud2Iterator<float> iter_z(cloud_msg, "z");

    // Step 4 — write each point into the message
    for(const auto & pt : world_points_)
    {
        *iter_x = pt[0];   // write X value
        *iter_y = pt[1];   // write Y value
        *iter_z = pt[2];   // write Z value

        // move cursor to next point
        ++iter_x;
        ++iter_y;
        ++iter_z;
    }
    cloud_pub_->publish(cloud_msg);
    RCLCPP_INFO(this->get_logger(),
        "Published cloud with %zu points",
        world_points_.size());

    world_points_.clear();
  }

  // Member variables
  sensor_msgs::msg::Image::SharedPtr latest_depth_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_sub_;
  rclcpp::Subscription<vision_msgs::msg::Detection2DArray>::SharedPtr detection_sub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_pub_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FusionNode>());
  rclcpp::shutdown();
  return 0;
}