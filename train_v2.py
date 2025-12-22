#!/usr/bin/env python3
"""
Ultra-simple training script - no multiprocessing, just single GPU training.
For Windows Python 3.14 compatibility.
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'

from pathlib import Path
from ultralytics import YOLO

print("=" * 60)
print("ATM Security - YOLOv8 GPU Training")
print("=" * 60)

# Configuration
config = {
    'weights': 'yolov8m.pt',
    'data': 'data_debug.yaml',  # Use training data for both train and val to ensure labels exist
    'epochs': 100,
    'batch': 32,
    'imgsz': 640,
    'device': 0,
    'project': 'runs/detect/atm_security',
    'name': 'train',
}

print("\nLoading model...")
model = YOLO(config['weights'])

print("\n🚀 Starting GPU training...\n")
results = model.train(
    data=config['data'],
    epochs=config['epochs'],
    batch=config['batch'],
    imgsz=config['imgsz'],
    device=config['device'],
    project=config['project'],
    name=config['name'],
    save=True,
    verbose=True,
    patience=15,
    val=True,
    plots=True,
    amp=False,
    workers=0,
    mosaic=True,
    close_mosaic=10,
)

print("\n✓ Training completed!")

# Copy best model
best_src = Path(config['project']) / config['name'] / 'weights' / 'best.pt'
if best_src.exists():
    Path('models').mkdir(exist_ok=True)
    import shutil
    best_dst = Path('models') / 'yolov8_atm_security_best.pt'
    shutil.copy(best_src, best_dst)
    print(f"✓ Best model saved: {best_dst}")
else:
    print(f"⚠ Best model not found at {best_src}")
