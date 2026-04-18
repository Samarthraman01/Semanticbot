import open3d as o3d
import numpy as np
import cv2
import os
import json

# ── Camera parameters from cam_params.json ──────────────────────────
W, H   = 1200, 680
FX, FY = 600.0, 600.0
CX, CY = 599.5, 339.5
SCALE  = 6553.5   # depth units → metres

BASE   = os.path.expanduser("~/semanticbot/data/Replica/office1")
RESULTS = f"{BASE}/results"

# ── Intrinsic matrix for Open3D ──────────────────────────────────────
intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, FX, FY, CX, CY)

# ── Count total frames ────────────────────────────────────────────────
frames = sorted([f for f in os.listdir(RESULTS) if f.startswith("frame")])
total  = len(frames)
print(f"Found {total} frames in office0")

# ── Open3D visualizer setup ──────────────────────────────────────────
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="SemanticBot — Live Point Cloud", 
                  width=1280, height=720)

pcd     = o3d.geometry.PointCloud()
added   = False

print("Starting playback — press Q in the Open3D window to quit")
print("Watch the point cloud build frame by frame...\n")

# ── Main loop — one frame at a time ──────────────────────────────────
for i in range(0, total, 5):   # every 5th frame for speed
    frame_id = f"{i:06d}"

    rgb_path   = f"{RESULTS}/frame{frame_id}.jpg"
    depth_path = f"{RESULTS}/depth{frame_id}.png"

    if not os.path.exists(rgb_path) or not os.path.exists(depth_path):
        continue

    # Read RGB and depth
    color = o3d.io.read_image(rgb_path)
    depth = o3d.io.read_image(depth_path)

    # Create RGBD image
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color, depth,
        depth_scale=SCALE,
        depth_trunc=5.0,        # ignore anything beyond 5 metres
        convert_rgb_to_intensity=False
    )

    # Project depth → 3D point cloud
    frame_pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd, intrinsic
    )

    # Update the visualizer
    pcd.points = frame_pcd.points
    pcd.colors = frame_pcd.colors

    if not added:
        vis.add_geometry(pcd)
        added = True
    else:
        vis.update_geometry(pcd)

    vis.poll_events()
    vis.update_renderer()

    print(f"Frame {i:04d}/{total} — {len(pcd.points):,} points", end="\r")

print("\nDone! Close the window to exit.")
vis.run()
vis.destroy_window()