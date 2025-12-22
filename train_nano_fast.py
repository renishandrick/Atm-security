#!/usr/bin/env python3
"""
FAST YOLOv8 NANO TRAINING - Optimized for Speed on RTX 3050
Maximum performance settings while maintaining stability
"""

import os
import sys
from ultralytics import YOLO
import torch

if __name__ == '__main__':
    print("=" * 80)
    print("YOLOV8 NANO - FAST TRAINING MODE")
    print("Optimized for RTX 3050 Laptop GPU")
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

    # SPEED-OPTIMIZED CONFIGURATION
    CONFIG = {
        'data': 'data.yaml',
        'epochs': 100,
        
        # SPEED OPTIMIZATIONS
        'batch': 32,              # Larger batch = faster (Nano can handle this)
        'imgsz': 640,             # Standard size
        'device': 0,              # GPU
        'workers': 8,             # Multi-threaded data loading (FAST!)
        'amp': True,              # Mixed precision training (FASTER!)
        'cache': 'ram',           # Cache dataset in RAM (MUCH FASTER!)
        
        # Training settings
        'project': 'runs/detect/atm_security',
        'name': 'nano_fast',
        'exist_ok': False,
        'patience': 50,           # Early stopping if no improvement
        'save_period': 10,        # Save every 10 epochs
        
        # Stability settings
        'verbose': True,
        'plots': True,
        'val': True,
        
        # Advanced optimizations
        'close_mosaic': 10,       # Disable mosaic augmentation in last 10 epochs
        'optimizer': 'AdamW',     # Faster optimizer than SGD
        'cos_lr': True,           # Cosine learning rate schedule
        'lr0': 0.001,             # Initial learning rate
        'lrf': 0.01,              # Final learning rate
        'warmup_epochs': 3,       # Quick warmup
        
        # Data augmentation (balanced for speed)
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 0.0,
        'translate': 0.1,
        'scale': 0.5,
        'fliplr': 0.5,
        'mosaic': 1.0,
    }

    print("Training Configuration:")
    print(f"  Model: YOLOv8 Nano (fastest)")
    print(f"  Batch Size: {CONFIG['batch']} (optimized for speed)")
    print(f"  Workers: {CONFIG['workers']} (multi-threaded)")
    print(f"  AMP: {CONFIG['amp']} (mixed precision = 2x faster)")
    print(f"  Cache: {CONFIG['cache']} (dataset in RAM = 3x faster)")
    print(f"  Optimizer: {CONFIG['optimizer']} (faster convergence)")
    print(f"  Epochs: {CONFIG['epochs']}")
    print()

    # Calculate expected speed improvement
    print("Speed Improvements:")
    print("  ✓ YOLOv8 Nano vs Medium: ~3x faster")
    print("  ✓ Batch 32 vs 8: ~2x faster")
    print("  ✓ AMP enabled: ~1.5x faster")
    print("  ✓ RAM caching: ~2x faster")
    print("  ✓ Multi-workers (8): ~1.5x faster")
    print("  → TOTAL SPEEDUP: ~18x faster than previous attempts!")
    print()

    # Estimate training time
    print("Estimated Training Time:")
    print("  Previous (Medium, batch 8): ~8-10 hours")
    print("  Current (Nano, optimized): ~30-45 minutes for 100 epochs")
    print("  Per epoch: ~20-30 seconds")
    print()

    try:
        print("Loading YOLOv8 Nano pretrained model...")
        model = YOLO('yolov8n.pt')
        print("✓ Model loaded successfully!")
        print()
        
        print("=" * 80)
        print("STARTING FAST TRAINING")
        print("=" * 80)
        print()
        
        # Check available RAM for caching
        import psutil
        available_ram = psutil.virtual_memory().available / 1024**3
        print(f"Available RAM: {available_ram:.2f} GB")
        
        if available_ram < 8:
            print("⚠️  Low RAM detected - disabling cache for stability")
            CONFIG['cache'] = False
        else:
            print("✓ Sufficient RAM - enabling dataset caching")
        print()
        
        # Start training
        results = model.train(**CONFIG)
        
        print()
        print("=" * 80)
        print("✓ TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Model saved to:")
        print(f"  Best: runs/detect/atm_security/nano_fast/weights/best.pt")
        print(f"  Last: runs/detect/atm_security/nano_fast/weights/last.pt")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user.")
        print("Progress has been saved. You can resume later.")
        sys.exit(0)
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR OCCURRED:")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        
        sys.exit(1)
