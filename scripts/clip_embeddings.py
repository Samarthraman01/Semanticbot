import torch
import cv2
import clip
import numpy as np
import open3d as o3d
import os
import pickle
from ultralytics import YOLO
from PIL import Image

# ── Paths ────────────────────────────────────────────────────────────
RESULTS = os.path.expanduser("~/semanticbot/data/Replica/office0/results")
TRAJ    = os.path.expanduser("~/semanticbot/data/Replica/office0/traj.txt")
OUTPUT  = os.path.expanduser("~/semanticbot/outputs/semantic_map.pkl")
os.makedirs(os.path.expanduser("~/semanticbot/outputs"), exist_ok=True)

# ── Camera parameters ─────────────────────────────────────────────────
W, H     = 1200, 680
FX, FY   = 600.0, 600.0
CX, CY   = 599.5, 339.5
SCALE    = 6553.5

# ── Classes ───────────────────────────────────────────────────────────
CLASSES = ["chair", "desk", "monitor", "keyboard",
           "door", "cabinet", "table", "sofa", "bed", "shelf"]

CLASS_COLORS = {
    "chair":    [1.0, 0.0, 0.0],
    "desk":     [0.0, 1.0, 0.0],
    "monitor":  [0.0, 0.0, 1.0],
    "keyboard": [1.0, 1.0, 0.0],
    "door":     [1.0, 0.5, 0.0],
    "cabinet":  [0.5, 0.0, 1.0],
    "table":    [0.0, 1.0, 1.0],
    "sofa":     [1.0, 0.0, 1.0],
    "bed":      [0.5, 1.0, 0.0],
    "shelf":    [0.0, 0.5, 1.0],
}

# ── Device ────────────────────────────────────────────────────────────
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {device}\n")

# ── Load models ───────────────────────────────────────────────────────
print("Loading YOLO-World...")
yolo = YOLO("yolov8s-worldv2.pt")
yolo.to(device)
yolo.set_classes(CLASSES)

print("Loading CLIP...")
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# ── Load camera poses ─────────────────────────────────────────────────
def load_poses(traj_path):
    """Read camera poses from traj.txt — one 4x4 matrix per line"""
    poses = []
    with open(traj_path) as f:
        for line in f:
            values = [float(x) for x in line.strip().split()]
            matrix = np.array(values).reshape(4, 4)
            poses.append(matrix)
    return poses

poses = load_poses(TRAJ)
print(f"Loaded {len(poses)} poses\n")

# ── Semantic map — list of detected objects ───────────────────────────
# Each entry: {label, position_3d, clip_embedding, color}
semantic_map = []

# ── Process frames ────────────────────────────────────────────────────
frames = sorted([f for f in os.listdir(RESULTS) if f.startswith("frame")])
print(f"Processing {len(frames)//20} frames (every 20th)...\n")

for fname in frames[::20]:
    frame_id  = int(fname.replace("frame", "").replace(".jpg", ""))
    rgb_path  = f"{RESULTS}/frame{frame_id:06d}.jpg"
    dep_path  = f"{RESULTS}/depth{frame_id:06d}.png"

    if not os.path.exists(dep_path) or frame_id >= len(poses):
        continue

    # Read images
    rgb_cv   = cv2.imread(rgb_path)
    rgb_pil  = Image.fromarray(cv2.cvtColor(rgb_cv, cv2.COLOR_BGR2RGB))
    depth    = cv2.imread(dep_path, cv2.IMREAD_UNCHANGED).astype(np.float32)
    depth_m  = depth / SCALE
    pose     = poses[frame_id]

    # Run YOLO-World
    results  = yolo(rgb_cv, verbose=False, conf=0.15)[0]
    if len(results.boxes) == 0:
        continue

    for box in results.boxes:
        cls_id = int(box.cls)
        label  = CLASSES[cls_id]
        conf   = float(box.conf)
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

        # ── Get 3D position — use centre of bounding box ──────────────
        cx_px = (x1 + x2) // 2
        cy_px = (y1 + y2) // 2
        cx_px = max(0, min(W-1, cx_px))
        cy_px = max(0, min(H-1, cy_px))
        d     = depth_m[cy_px, cx_px]

        if d <= 0.1 or d > 8.0:
            continue

        # Project centre pixel to 3D
        X = (cx_px - CX) * d / FX
        Y = (cy_px - CY) * d / FY
        Z = d

        # Transform to world coordinates using camera pose
        point_cam   = np.array([X, Y, Z, 1.0])
        point_world = pose @ point_cam

        # ── Get CLIP embedding for this detection ──────────────────────
        # Crop the detected region from the RGB image
        if x2 <= x1 or y2 <= y1:
            continue
        crop = rgb_pil.crop((x1, y1, x2, y2))

        # Preprocess and encode with CLIP
        with torch.no_grad():
            crop_tensor = clip_preprocess(crop).unsqueeze(0).to(device)
            embedding   = clip_model.encode_image(crop_tensor)
            embedding   = embedding / embedding.norm(dim=-1, keepdim=True)
            embedding   = embedding.cpu().numpy().flatten()

        # ── Store in semantic map ──────────────────────────────────────
        semantic_map.append({
            "label":     label,
            "position":  point_world[:3],
            "embedding": embedding,
            "color":     CLASS_COLORS[label],
            "confidence": conf,
            "frame_id":  frame_id,
        })

        print(f"  Frame {frame_id:04d} → {label:12s} {conf:.0%} "
              f"at ({point_world[0]:.2f}, {point_world[1]:.2f}, {point_world[2]:.2f})")

# ── Save the semantic map ─────────────────────────────────────────────
with open(OUTPUT, "wb") as f:
    pickle.dump(semantic_map, f)

print(f"\n{'='*50}")
print(f"Semantic map saved to: {OUTPUT}")
print(f"Total objects stored: {len(semantic_map)}")
print(f"Each object has: label + 3D position + 512-dim CLIP embedding")

# ── Quick visualization ───────────────────────────────────────────────
print("\nOpening 3D viewer...")

# Load room mesh
mesh     = o3d.io.read_triangle_mesh(
    os.path.expanduser("~/semanticbot/data/Replica/office0_mesh.ply"))
mesh.compute_vertex_normals()
room_pcd = mesh.sample_points_uniformly(number_of_points=200000)
grey     = np.ones((200000, 3)) * 0.6
room_pcd.colors = o3d.utility.Vector3dVector(grey)

# Plot each object as a coloured sphere at its 3D position
geometries = [room_pcd]
for obj in semantic_map:
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.08)
    sphere.translate(obj["position"])
    sphere.paint_uniform_color(obj["color"])
    geometries.append(sphere)

o3d.visualization.draw_geometries(
    geometries,
    window_name="SemanticBot — Objects with CLIP Embeddings",
    width=1280,
    height=720
)