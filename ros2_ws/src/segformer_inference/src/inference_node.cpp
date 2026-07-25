#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vector>
#include <memory>
#include <chrono>

using namespace std;

class inference_node : public rclcpp::Node {
public:
    inference_node() : Node("inference_node") {
    image_sub_ = create_subscription<sensor_msgs::msg::Image>(
        "/camera/image/raw", 10,
        [this](const sensor_msgs::msg::Image::SharedPtr msg) {
            image_callback(msg);
        }
    );
    RCLCPP_INFO(this->get_logger(), "Inference node has been started.");
}

private:
    void image_callback(const sensor_msgs::msg::Image::SharedPtr image_msg){
        RCLCPP_INFO(get_logger(), "recieved image with: %d x %d" , image_msg->width, image_msg->height);
    }

    //member viariables
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = make_shared<inference_node>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}