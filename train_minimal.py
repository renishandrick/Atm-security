#!/usr/bin/env python3
"""Minimal training script for testing."""

from ultralytics import YOLO

print("🚀 Starting YOLOv8 training...")
model = YOLO('yolov8m.pt')

# Train with minimal config
results = model.train(
    data='data_debug.yaml',
    epochs=100,
    batch=32,
    imgsz=640,
    device=0,
    project='runs/detect/atm_final',
    name='exp1',
    verbose=True,
    workers=0,
    patience=15,
)

print("✓ Done! Results saved.")
print(f"Output: runs/detect/atm_final/exp1")
