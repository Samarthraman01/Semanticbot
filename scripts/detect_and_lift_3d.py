import torch
import cv2
import numpy as np
import open3d as o3d
import os
from ultralytics import YOLO

def load_poses(traj_path):
    """Read camera poses from traj.txt — one 4x4 matrix per line"""
    poses = []
    with open(traj_path) as f:
        for line in f:
            values = [float(x) for x in line.strip().split()]
            matrix = np.array(values).reshape(4, 4)
            poses.append(matrix)
    return poses
# ── Paths ────────────────────────────────────────────────────────────
RESULTS = os.path.expanduser("~/semanticbot/data/Replica/office0/results")
TRAJ = os.path.expanduser("~/semanticbot/data/Replica/office0/traj.txt")
poses = load_poses(TRAJ)
print(f"Loaded {len(poses)} camera poses")

# ── Camera parameters from cam_params.json ───────────────────────────
W, H     = 1200, 680
FX, FY   = 600.0, 600.0
CX, CY   = 599.5, 339.5
SCALE    = 6553.5

# ── Colour per class for 3D visualization ────────────────────────────
CLASSES = ["chair", "desk", "monitor", "keyboard", "door", "cabinet",
           "table", "sofa", "bed", "shelf"]

CLASS_COLORS = {
    "chair":    [1.0, 0.0, 0.0],   # red
    "desk":     [0.0, 1.0, 0.0],   # green
    "monitor":  [0.0, 0.0, 1.0],   # blue
    "keyboard": [1.0, 1.0, 0.0],   # yellow
    "door":     [1.0, 0.5, 0.0],   # orange
    "cabinet":  [0.5, 0.0, 1.0],   # purple
    "table":    [0.0, 1.0, 1.0],   # cyan
    "sofa":     [1.0, 0.0, 1.0],   # magenta
    "bed":      [0.5, 1.0, 0.0],   # lime
    "shelf":    [0.0, 0.5, 1.0],   # sky blue
}

# ── Load YOLO-World ───────────────────────────────────────────────────
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {device}")
print("Loading YOLO-World...")

model = YOLO("yolov8s-worldv2.pt")
model.to(device)
model.set_classes(CLASSES)

# ── Camera intrinsic for Open3D ───────────────────────────────────────
intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, FX, FY, CX, CY)

# ── This will hold ALL semantic points across all frames ──────────────
all_points = []
all_colors = []

print("Processing frames...\n")

# ── Process every 20th frame ─────────────────────────────────────────
frames = sorted([f for f in os.listdir(RESULTS) if f.startswith("frame")])

for fname in frames[::20]:
    frame_id = fname.replace("frame", "").replace(".jpg", "")
    rgb_path   = f"{RESULTS}/frame{frame_id}.jpg"
    depth_path = f"{RESULTS}/depth{frame_id}.png"

    if not os.path.exists(depth_path):
        continue

    # Read RGB and depth
    rgb   = cv2.imread(rgb_path)
    depth = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED).astype(np.float32)

    # Run YOLO-World detection
    results = model(rgb, verbose=False, conf=0.15)[0]

    if len(results.boxes) == 0:
        continue

    # Convert depth to metres
    depth_m = depth / SCALE

    # Get camera pose for this frame
    frame_idx = int(frame_id)
    if frame_idx >= len(poses):
        continue
    pose = poses[frame_idx]  # 4x4 transformation matrix

    for box in results.boxes:
        cls_id = int(box.cls)
        label  = CLASSES[cls_id]
        color  = CLASS_COLORS[label]
        conf   = float(box.conf)

        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

        for v in range(max(0, y1), min(H, y2), 4):
            for u in range(max(0, x1), min(W, x2), 4):
                d = depth_m[v, u]
                if d <= 0.1 or d > 8.0:
                    continue

                # Project to 3D in camera space
                X = (u - CX) * d / FX
                Y = (v - CY) * d / FY
                Z = d

                # Apply camera pose → transform to world space
                point_cam = np.array([X, Y, Z, 1.0])
                point_world = pose @ point_cam

                all_points.append(point_world[:3])
                all_colors.append(color)

    detected = [CLASSES[int(b.cls)] for b in results.boxes]
    print(f"Frame {frame_id} → {detected}")

# ── Load the full room mesh for context ──────────────────────────────
print("Loading room mesh for context...")
mesh_path = os.path.expanduser("~/semanticbot/data/Replica/office0_mesh.ply")
try:
    mesh = o3d.io.read_triangle_mesh(mesh_path)
    if mesh.is_empty():
        raise ValueError("Mesh is empty")
    mesh.compute_vertex_normals()

    # Convert mesh to point cloud for easier display alongside detections
    room_pcd = mesh.sample_points_uniformly(number_of_points=200000)

    # Make the room grey so semantic colours stand out
    grey = np.ones((200000, 3)) * 0.6
    room_pcd.colors = o3d.utility.Vector3dVector(grey)
    has_room_mesh = True
except Exception as e:
    print(f"Warning: Could not load room mesh ({e})")
    has_room_mesh = False

# ── Semantic point cloud ──────────────────────────────────────────────
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(np.array(all_points))
pcd.colors = o3d.utility.Vector3dVector(np.array(all_colors))

print(f"Semantic points: {len(all_points):,}")
if has_room_mesh:
    print("Opening viewer — grey = room geometry, colours = detected objects")
else:
    print("Opening viewer — colours = detected objects (room mesh not loaded)")
print("Rotate with mouse, scroll to zoom\n")

# ── Show both together ────────────────────────────────────────────────
geoms = [pcd]
if has_room_mesh:
    geoms.insert(0, room_pcd)

o3d.visualization.draw_geometries(
    geoms,
    window_name="SemanticBot — Semantic 3D Map",
    width=1280,
    height=720
)