#!/usr/bin/env python3
import sys
print("Python:", sys.version)

print("\n--- Checking Imports ---")
try:
    import torch
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count()
    print(f"✓ PyTorch {torch.__version__}")
    print(f"  CUDA available: {cuda_available}")
    print(f"  Device count: {device_count}")
    if cuda_available and device_count > 0:
        print(f"  Device 0: {torch.cuda.get_device_name(0)}")
        print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
except Exception as e:
    print(f"✗ torch error: {e}")
    sys.exit(1)

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except Exception as e:
    print(f"✗ cv2 error: {e}")

try:
    from ultralytics import YOLO
    print("✓ Ultralytics YOLO available")
except Exception as e:
    print(f"✗ ultralytics error: {e}")

print("\n✓ All systems ready for GPU training!")
