#!/usr/bin/env python3
"""
FRESH START TRAINING - New directory, no corrupted checkpoints
Conservative settings for maximum stability
"""

import os
import sys
from ultralytics import YOLO
import torch

print("=" * 80)
print("YOLOV8 TRAINING - FRESH START (NO CORRUPTED CHECKPOINTS)")
print("=" * 80)
print()

# System check
print("System Check:")
print(f"  Python: {sys.version.split()[0]}")
print(f"  PyTorch: {torch.__version__}")
print(f"  CUDA: {torch.version.cuda}")
print(f"  GPU: {torch.cuda.get_device_name(0)}")
print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
print()

# Ultra-conservative configuration
CONFIG = {
    'data': 'data.yaml',
    'epochs': 100,
    'batch': 8,  # VERY small batch for maximum stability
    'imgsz': 640,
    'device': 0,
    'project': 'runs/detect/atm_security',
    'name': 'train_fresh',  # NEW directory - no corrupted files
    'exist_ok': False,  # Force new directory
    'patience': 100,  # Very patient
    'workers': 0,  # Single worker
    'amp': False,  # No AMP
    'verbose': True,
    'save_period': 5,  # Save every 5 epochs
    'cache': False,  # Don't cache to avoid memory issues
    'close_mosaic': 10  # Disable mosaic augmentation in last 10 epochs
}

print("Training Configuration:")
for key, value in CONFIG.items():
    print(f"  {key}: {value}")
print()

try:
    print("Loading YOLOv8 Medium pretrained model...")
    model = YOLO('yolov8m.pt')
    print("Model loaded successfully!")
    print()
    
    print("=" * 80)
    print("STARTING FRESH TRAINING")
    print("=" * 80)
    print()
    
    # Start training
    results = model.train(**CONFIG)
    
    print()
    print("=" * 80)
    print("SUCCESS! Training completed!")
    print("=" * 80)
    
except KeyboardInterrupt:
    print("\n\nTraining interrupted by user.")
    print("Progress has been saved. You can resume later.")
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 80)
    print("ERROR OCCURRED:")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print()
    
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    print("=" * 80)
    
    sys.exit(1)
