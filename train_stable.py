#!/usr/bin/env python3
"""
Ultra-stable training with conservative settings
Smaller batch size for better stability
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch

print("=" * 80)
print("YOLOV8 TRAINING - ULTRA STABLE MODE")
print("=" * 80)
print()

# Check CUDA
print("Checking system...")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
print()

# Use SMALLER batch size for stability
BATCH_SIZE = 16  # Reduced from 32 for better stability
EPOCHS = 100
WORKERS = 0  # Single worker to avoid multiprocessing issues

print("Configuration:")
print(f"  Batch Size: {BATCH_SIZE} (reduced for stability)")
print(f"  Epochs: {EPOCHS}")
print(f"  Workers: {WORKERS}")
print(f"  AMP: False (disabled for stability)")
print()

# Check for checkpoint
checkpoint_path = Path('runs/detect/atm_security/train_gpu5/weights/last.pt')

try:
    if checkpoint_path.exists():
        print(f"Found checkpoint: {checkpoint_path}")
        print("Attempting to resume from checkpoint...")
        print()
        
        model = YOLO(str(checkpoint_path))
        
        # Resume with more conservative settings
        results = model.train(
            resume=True,
            batch=BATCH_SIZE,  # Override with smaller batch
            workers=WORKERS,
            amp=False,
            verbose=True,
            patience=50,  # More patience
            save_period=1  # Save every epoch
        )
        
    else:
        print("No checkpoint found. Starting fresh training...")
        print()
        
        model = YOLO('yolov8m.pt')
        
        results = model.train(
            data='data.yaml',
            epochs=EPOCHS,
            batch=BATCH_SIZE,
            imgsz=640,
            device=0,
            project='runs/detect/atm_security',
            name='train_stable',
            exist_ok=True,
            patience=50,
            workers=WORKERS,
            amp=False,
            verbose=True,
            save_period=1
        )
    
    print()
    print("=" * 80)
    print("SUCCESS! Training completed!")
    print("=" * 80)
    
except KeyboardInterrupt:
    print("\n\nTraining interrupted by user.")
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 80)
    print("ERROR OCCURRED:")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print()
    
    # Try to get more details
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    print("=" * 80)
    
    print()
    print("TROUBLESHOOTING SUGGESTIONS:")
    print("1. Check if dataset files are accessible")
    print("2. Verify CUDA/GPU is working: nvidia-smi")
    print("3. Try reducing batch size further")
    print("4. Check disk space")
    print("=" * 80)
    
    sys.exit(1)
