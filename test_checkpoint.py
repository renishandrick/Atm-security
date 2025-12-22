#!/usr/bin/env python3
"""
Test checkpoint validity and create fresh start if needed
"""

import torch
from pathlib import Path
from ultralytics import YOLO

print("=" * 80)
print("CHECKPOINT VALIDATION TEST")
print("=" * 80)
print()

checkpoint_path = Path('runs/detect/atm_security/train_gpu5/weights/last.pt')

if checkpoint_path.exists():
    print(f"Checkpoint found: {checkpoint_path}")
    print(f"Size: {checkpoint_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        print("Loading checkpoint with PyTorch...")
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        print(f"Epoch in checkpoint: {checkpoint.get('epoch', 'unknown')}")
        print(f"Best fitness: {checkpoint.get('best_fitness', 'unknown')}")
        print("Checkpoint structure looks valid!")
        print()
        
        print("Testing YOLO model load...")
        model = YOLO(str(checkpoint_path))
        print("YOLO model loaded successfully!")
        print()
        
        print("=" * 80)
        print("CHECKPOINT IS VALID - Can resume from epoch", checkpoint.get('epoch', 'unknown'))
        print("=" * 80)
        
    except Exception as e:
        print("=" * 80)
        print("ERROR: Checkpoint is CORRUPTED!")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("RECOMMENDATION: Start fresh training from pretrained weights")
        print("=" * 80)
        
else:
    print("No checkpoint found - will start fresh training")
