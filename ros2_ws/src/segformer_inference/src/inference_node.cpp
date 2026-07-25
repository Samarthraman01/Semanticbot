#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vector>
#include <memory>
#include <chrono>
#include <onnxruntime_cxx_api.h>

using namespace std;

class inference_node : public rclcpp::Node {
public:
    inference_node() : Node("inference_node"),
        env_(ORT_LOGGING_LEVEL_WARNING, "inference"),
        session_(env_,
                 "/home/samarthws/Semanticbot/models/segformer_b2.onnx",
                 Ort::SessionOptions{})
    {
        image_sub_ = create_subscription<sensor_msgs::msg::Image>(
            "/camera/image/raw", 10,
            [this](const sensor_msgs::msg::Image::SharedPtr msg) {
                image_callback(msg);
            }
        );
        RCLCPP_INFO(get_logger(), "SegFormer model loaded!");
        RCLCPP_INFO(get_logger(), "Inference node started!");
    }

private:
    void image_callback(const sensor_msgs::msg::Image::SharedPtr image_msg) {
        RCLCPP_INFO(get_logger(), "received image: %d x %d",
                    image_msg->width, image_msg->height);
    }

    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
    Ort::Env env_;
    Ort::Session session_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = make_shared<inference_node>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}