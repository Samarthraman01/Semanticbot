# SemanticBot 🤖

Open-vocabulary semantic 3D mapping for indoor robots.

## What it does
Builds a 3D map of an indoor environment where every object is 
labelled automatically using natural language. Query the map with 
plain English — "find the wheelchair" — and get a 3D location back.

## Tech stack
- ROS 2 Humble (Docker)
- YOLO-World — open-vocabulary object detection
- CLIP — vision-language embeddings
- Open3D — 3D point cloud processing
- Python + C++ (ROS 2 fusion node)

## Progress
- [x] Week 1 — Environment setup (Docker, ROS 2, Open3D)
- [x] Week 2 — Replica RGB-D dataset pipeline
- [x] Week 3 — YOLO-World semantic detection + 3D lifting
- [ ] Week 4 — CLIP embeddings per object
- [ ] Week 5 — C++ fusion node
- [ ] Week 6 — Semantic voxel map
- [ ] Week 7 — Natural language query engine
- [ ] Week 8 — Demo video + deployment

## Dataset
Uses the Replica dataset (Meta Reality Labs) for photorealistic 
indoor RGB-D sequences.

## Author
Samarth Raman Ghanate — M.Sc. Electromobility Engineering, FAU Erlangen
