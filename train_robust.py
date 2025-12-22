#!/usr/bin/env python3
"""
Robust training script with detailed logging
Resumes from last checkpoint with better error handling
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch

print("=" * 80)
print("YOLOV8 TRAINING - ROBUST RESUME")
print("=" * 80)
print()

# Check CUDA
print("Checking CUDA...")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
print()

# Find checkpoint
checkpoint_path = Path('runs/detect/atm_security/train_gpu5/weights/last.pt')

if checkpoint_path.exists():
    print(f"✓ Found checkpoint: {checkpoint_path}")
    print(f"  File size: {checkpoint_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        print("Loading model from checkpoint...")
        model = YOLO(str(checkpoint_path))
        print("✓ Model loaded successfully")
        print()
        
        print("Starting training with resume=True...")
        print("This will continue from where it left off")
        print()
        print("-" * 80)
        
        # Resume training
        results = model.train(
            resume=True,
            verbose=True
        )
        
        print()
        print("=" * 80)
        print("✓ TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERROR DURING TRAINING:")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        print("Full traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        sys.exit(1)
        
else:
    print(f"❌ Checkpoint not found: {checkpoint_path}")
    print()
    print("Starting fresh training instead...")
    print()
    
    try:
        model = YOLO('yolov8m.pt')
        
        results = model.train(
            data='data.yaml',
            epochs=100,
            batch=32,
            imgsz=640,
            device=0,
            project='runs/detect/atm_security',
            name='train_gpu5',
            exist_ok=True,
            patience=20,
            workers=0,
            amp=False,
            verbose=True
        )
        
        print()
        print("=" * 80)
        print("✓ TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERROR DURING TRAINING:")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        print("Full traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        sys.exit(1)
