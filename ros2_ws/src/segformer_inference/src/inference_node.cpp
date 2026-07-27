#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vector>
#include <memory>
#include <chrono>
#include <onnxruntime_cxx_api.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <sensor_msgs/image_encodings.hpp>

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

    //Image processing function
    void image_callback(const sensor_msgs::msg::Image::SharedPtr image_msg) {
        cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(image_msg, sensor_msgs::image_encodings::RGB8);
        cv::Mat input_image = cv_ptr->image;

        //resize to 512×512
        cv::Mat resized_image;
        cv::resize(input_image, resized_image, cv::Size(512, 512));

        //normalize the image
        resized_image.convertTo(resized_image, CV_32F, 1.0 / 255.0);

        //substract mean and divide by standard deviation
        float mean[3] = {0.485f, 0.456f, 0.406f};
        float std[3] = {0.229f, 0.224f, 0.225f};

        vector<cv::Mat> channels(3);
        cv::split(resized_image, channels);

        // Normalize each channel
        for (int c = 0; c < 3; ++c) {
            channels[c] = (channels[c] - mean[c]) / std[c];
        }

        //merge channels into CHW float array
        int H = 512, W = 512, C = 3;
        vector<float> input_data(C * H * W);

        // Copy the normalized data into the input_data vector in CHW format
        for (int c = 0; c < C; c++) {
            memcpy(
                input_data.data() + c * H * W,
                channels[c].data,
                H * W * sizeof(float)
            );
        }
       

        RCLCPP_INFO(get_logger(), "Received image: %d x %d", resized_image.cols, resized_image.rows);
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