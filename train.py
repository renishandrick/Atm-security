# train.py
from ultralytics import YOLO
import os

print("🚀 Starting Training...")
print("This will take 30-60 minutes on your RTX 3050")

# Load model
model = YOLO('yolov8n.pt')

# Train model
results = model.train(
    data='data.yaml',  # Make sure this file exists
    epochs=50,
    imgsz=640,
    batch=8,
    device=0,  # Use your GPU
    patience=10,
    save=True,
    verbose=True
)

print("✅ Training Completed!")
print("📁 Model saved in: runs/detect/train/weights/best.pt")