# SemanticBot 🤖
> Open-vocabulary semantic 3D mapping for indoor robots — find any object with natural language

[![ROS 2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org)
[![C++](https://img.shields.io/badge/C%2B%2B-17-orange)](https://isocpp.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## The problem

Indoor robots can navigate and avoid obstacles but they are semantically blind. They know where things are geometrically but have no idea what those things are. Ask a robot to find the wheelchair and it cannot — it only sees distances, not meaning. SemanticBot bridges that gap.

---

## What it does

SemanticBot builds a queryable semantic 3D map of an indoor environment. Every point in the map carries a class label, a CLIP language fingerprint, and a real 3D world position. Query the map in plain English and get a 3D location back — no retraining, no hardcoded labels, any object, any description.

---

## Architecture
## Architecture

```mermaid
flowchart TD
    A[🗂️ Replica RGB-D Dataset\noffice0 — RGB frames + depth images + camera poses] --> B

    B[📷 frame_reader.py\nRGB + depth + intrinsics → 3D point cloud\nOpen3D viewer] --> C

    C[🔍 detect_objects.py\nYOLO-World open-vocabulary detection\n2D bounding boxes + class labels] --> D

    D[📐 detect_and_lift_3d.py\n2D boxes + depth + pose matrix\n→ semantic coloured 3D point cloud] --> E

    E[🧠 clip_embeddings.py\nOpenAI CLIP encodes each detection\n→ 512-dim language fingerprint per object\nsaved to semantic_map.pkl] --> F

    F[🔎 query_map.py\ntext query → CLIP text encoding\n→ cosine similarity search\n→ 3D location highlighted in Open3D] 

    D --> G[⚙️ fusion_node.cpp\nC++ ROS 2 node\ndepth + detections → world 3D points\npublishes /semantic/pointcloud]

    style A fill:#2d6a4f,color:#fff
    style B fill:#1d3557,color:#fff
    style C fill:#6a0572,color:#fff
    style D fill:#6a0572,color:#fff
    style E fill:#b5451b,color:#fff
    style F fill:#b5451b,color:#fff
    style G fill:#1d3557,color:#fff
```

---

## Tech stack

| Component | Technology |
|-----------|------------|
| Robot middleware | ROS 2 Humble |
| Object detection | YOLO-World (open-vocabulary) |
| Vision-language model | OpenAI CLIP (ViT-B/32) |
| 3D processing | Open3D |
| Neural network framework | PyTorch 2.2 + Apple MPS |
| C++ perception node | rclcpp, sensor_msgs, vision_msgs |
| Dataset | Replica (Meta Reality Labs) |
| Environment | Docker + Ubuntu 22.04 |

---

## Results

- 688 objects detected and stored across one indoor office scene
- Natural language queries work for both direct and indirect descriptions
- C++ ROS 2 fusion node publishes semantic point clouds on /semantic/pointcloud
- Runs on Apple M2 Pro with MPS GPU acceleration — no NVIDIA GPU required

---

## How to run

```bash
# Clone the repo
git clone https://github.com/Samarthraman01/Semanticbot.git
cd Semanticbot

# Create conda environment
conda create -n semanticbot python=3.11 -y
conda activate semanticbot
pip install open3d torch torchvision ultralytics

# Build semantic map
python3 scripts/clip_embeddings.py

# Query with natural language
python3 scripts/query_map.py

# Run C++ ROS 2 fusion node (requires Docker)
docker run -it --rm -v $(pwd):/workspace ros:humble bash
source /opt/ros/humble/setup.bash
cd /workspace/ros2_ws && colcon build
ros2 run semantic_fusion fusion_node
```

---

## Author

**Samarth Raman Ghanate**
M.Sc. Electromobility Engineering — FAU Erlangen-Nürnberg
Research Assistant — Siemens Healthineers

[LinkedIn](https://linkedin.com/in/yourprofile) · [GitHub](https://github.com/Samarthraman01)