#!/usr/bin/env python3
"""
Workaround for Python 3.14 + PyTorch GPU issue.
Use smaller model and different training approach.
"""

from ultralytics import YOLO

print("Loading YOLOv8 Nano (smaller model for stability)...")
model = YOLO('yolov8n.pt')  # Nano instead of Medium

print("Starting training with GPU...\n")

# Simpler training config to avoid gradient issues
results = model.train(
    data='data_debug.yaml',
    epochs=50,  # Reduce epochs for now
    batch=16,   # Reduce batch size
    imgsz=640,
    device=0,
    project='runs/detect/atm_final',
    name='nano_model',
    workers=0,
    patience=10,
    verbose=True,
)

print("\n✓ Training complete!")
print("Best model: runs/detect/atm_final/nano_model/weights/best.pt")
