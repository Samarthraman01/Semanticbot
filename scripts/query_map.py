import pickle
import torch
import clip
import numpy as np
import open3d as o3d
import os

# ── Load the semantic map ─────────────────────────────────────────────
MAP_PATH  = os.path.expanduser("~/semanticbot/outputs/semantic_map.pkl")
MESH_PATH = os.path.expanduser("~/semanticbot/data/Replica/office0_mesh.ply")

with open(MAP_PATH, "rb") as f:
    semantic_map = pickle.load(f)

print(f"Loaded semantic map — {len(semantic_map)} objects")

# ── Load CLIP for text encoding ───────────────────────────────────────
device = "mps" if torch.backends.mps.is_available() else "cpu"
clip_model, _ = clip.load("ViT-B/32", device=device)
print(f"CLIP loaded on: {device}")

# ── Load room mesh ────────────────────────────────────────────────────
mesh     = o3d.io.read_triangle_mesh(MESH_PATH)
mesh.compute_vertex_normals()
room_pcd = mesh.sample_points_uniformly(number_of_points=200000)
grey     = np.ones((200000, 3)) * 0.6
room_pcd.colors = o3d.utility.Vector3dVector(grey)

# ── Query function ────────────────────────────────────────────────────
def query(text, top_k=5):
    """
    Takes a natural language query and returns the top_k
    most similar objects in the semantic map.
    """
    # Encode the text query with CLIP
    with torch.no_grad():
        tokens    = clip.tokenize([text]).to(device)
        text_emb  = clip_model.encode_text(tokens)
        text_emb  = text_emb / text_emb.norm(dim=-1, keepdim=True)
        text_emb  = text_emb.cpu().numpy().flatten()

    # Compare text embedding against every object embedding
    # using cosine similarity
    scores = []
    for i, obj in enumerate(semantic_map):
        img_emb    = obj["embedding"]
        similarity = float(np.dot(text_emb, img_emb))
        scores.append((similarity, i))

    # Sort by similarity — highest first
    scores.sort(reverse=True)
    return scores[:top_k]

# ── Visualize query results ───────────────────────────────────────────
def visualize_results(query_text, results):
    """Show the room with query results highlighted in yellow."""
    geometries = [room_pcd]

    # Draw all objects as small grey spheres
    for obj in semantic_map:
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.06)
        sphere.translate(obj["position"])
        sphere.paint_uniform_color([0.5, 0.5, 0.5])
        geometries.append(sphere)

    # Draw top results as large bright yellow spheres
    print(f"\nTop matches for '{query_text}':")
    for rank, (score, idx) in enumerate(results):
        obj = semantic_map[idx]
        pos = obj["position"]

        # Large yellow sphere for the best match
        size   = 0.18 if rank == 0 else 0.12
        color  = [1.0, 1.0, 0.0] if rank == 0 else [1.0, 0.8, 0.0]

        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=size)
        sphere.translate(pos)
        sphere.paint_uniform_color(color)
        geometries.append(sphere)

        print(f"  #{rank+1} {obj['label']:12s} "
              f"score={score:.3f} "
              f"at ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    o3d.visualization.draw_geometries(
        geometries,
        window_name=f"Query: '{query_text}'",
        width=1280,
        height=720
    )

# ── Interactive query loop ────────────────────────────────────────────
print("\n" + "="*50)
print("SemanticBot — Language Query Engine")
print("="*50)
print("Type any object to find it in the 3D map.")
print("Examples: chair, desk, monitor, something to sit on")
print("Type 'quit' to exit\n")

while True:
    query_text = input("Search: ").strip()

    if query_text.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    if not query_text:
        continue

    results = query(query_text, top_k=5)
    visualize_results(query_text, results)
    print("\nClose the 3D window to search again.")