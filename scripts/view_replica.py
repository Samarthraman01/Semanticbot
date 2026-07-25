import open3d as o3d
import os

replica_path = os.path.expanduser("~/semanticbot/data/Replica")

# Load office0 mesh directly
ply_path = f"{replica_path}/office0_mesh.ply"
print(f"Loading: {ply_path}")

mesh = o3d.io.read_triangle_mesh(ply_path)
mesh.compute_vertex_normals()

print(f"Vertices:  {len(mesh.vertices)}")
print(f"Triangles: {len(mesh.triangles)}")
print("Opening viewer — use mouse to rotate, scroll to zoom...")

o3d.visualization.draw_geometries(
    [mesh],
    window_name="Replica — office0",
    width=1280,
    height=720
)