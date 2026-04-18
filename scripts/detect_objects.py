import cv2
import torch
from ultralytics import YOLO
import os

# ── Setup ────────────────────────────────────────────────────────────
FRAMES_PATH = os.path.expanduser(
    "~/semanticbot/data/Replica/office0/results"
)

# Use M2 GPU if available
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Running on: {device}")

# ── Load YOLO-World model ─────────────────────────────────────────────
# Downloads automatically on first run (~100MB)
print("Loading YOLO-World model...")
model = YOLO("yolov8s-worldv2.pt")
model.to(device)

# ── Tell it what objects to look for ─────────────────────────────────
# This is the open-vocabulary part — you can put ANYTHING here
objects_to_find = [
    "chair", "desk", "monitor", "keyboard",
    "door", "window", "cabinet", "lamp"
]
model.set_classes(objects_to_find)
print(f"Looking for: {objects_to_find}\n")

# ── Run detection on every 10th frame ────────────────────────────────
frames = sorted([
    f for f in os.listdir(FRAMES_PATH)
    if f.startswith("frame")
])

for i, fname in enumerate(frames[::10]):  # every 10th frame
    frame_path = f"{FRAMES_PATH}/{fname}"
    frame = cv2.imread(frame_path)

    # Run YOLO-World
    results = model(frame, verbose=False)[0]

    # Draw detections on the frame
    annotated = results.plot()

    # Show it
    cv2.imshow("SemanticBot — YOLO-World Detections", annotated)

    # Print what was found
    if len(results.boxes) > 0:
        for box in results.boxes:
            label = objects_to_find[int(box.cls)]
            confidence = float(box.conf)
            print(f"Frame {i*10:04d} → {label} ({confidence:.0%} confident)")

    # Press Q to quit, any key to continue
    key = cv2.waitKey(200)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
print("\nDone!")