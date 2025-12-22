#!/usr/bin/env python3
"""
OPTIMIZED TRAINING - Batch 16 for 2x speed
~1.5 days instead of 3 days
"""

import sys
from ultralytics import YOLO
import torch

print("=" * 80)
print("YOLOV8 TRAINING - OPTIMIZED (BATCH 16)")
print("=" * 80)
print()

print("System:")
print(f"  PyTorch: {torch.__version__}")
print(f"  CUDA: {torch.version.cuda}")
print(f"  GPU: {torch.cuda.get_device_name(0)}")
print()

CONFIG = {
    'data': 'data.yaml',
    'epochs': 100,
    'batch': 16,  # 2x faster than batch 8
    'imgsz': 640,
    'device': 0,
    'project': 'runs/detect/atm_security',
    'name': 'train_optimized',
    'exist_ok': False,
    'patience': 100,
    'workers': 0,
    'amp': False,
    'verbose': True,
    'save_period': 5,
    'cache': False
}

print("Configuration:")
print(f"  Batch: {CONFIG['batch']} (2x faster!)")
print(f"  Epochs: {CONFIG['epochs']}")
print(f"  Expected: ~1.5 days")
print()

try:
    print("Loading model...")
    model = YOLO('yolov8m.pt')
    print()
    
    print("=" * 80)
    print("STARTING TRAINING")
    print("=" * 80)
    print()
    
    results = model.train(**CONFIG)
    
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    
except KeyboardInterrupt:
    print("\n\nInterrupted by user.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
