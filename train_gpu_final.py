#!/usr/bin/env python3
"""
Final GPU training script for ATM Security (face, mask, helmet detection).
Trains YOLOv8 on GPU with best practices and saves the trained model.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Train YOLOv8 for ATM Security on GPU')
    parser.add_argument('--weights', default='yolov8m.pt', help='Pretrained weights (yolov8n/s/m/l/x)')
    parser.add_argument('--data', default='data.yaml', help='Data config file')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=32, help='Batch size (increase for GPU)')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--device', default='0', help='GPU device (0, 1, etc) or cpu')
    parser.add_argument('--project', default='runs/detect/atm_security', help='Project name')
    parser.add_argument('--name', default='train_gpu', help='Experiment name')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--save-dir', default='models', help='Directory to save best model')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.data):
        print(f"❌ Error: Data config file not found: {args.data}")
        sys.exit(1)
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ GPU count: {torch.cuda.device_count()}")
            print(f"✓ Device 0: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        print(f"❌ PyTorch error: {e}")
        sys.exit(1)
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics YOLO available")
    except Exception as e:
        print(f"❌ Ultralytics error: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print(f"Training configuration:")
    print(f"  Weights: {args.weights}")
    print(f"  Data: {args.data}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch}")
    print(f"  Image size: {args.imgsz}")
    print(f"  Device: {args.device}")
    print(f"  Project: {args.project}")
    print("="*60 + "\n")
    
    # Load model
    print(f"Loading model: {args.weights}")
    model = YOLO(args.weights)
    
    # Prepare training arguments
    train_args = {
        'data': args.data,
        'epochs': args.epochs,
        'batch': args.batch,
        'imgsz': args.imgsz,
        'device': args.device,
        'project': args.project,
        'name': args.name,
        'save': True,
        'patience': 20,  # Early stopping patience
        'verbose': True,
        'close_mosaic': 10,  # Close mosaic augmentation in last 10 epochs
        'amp': False,  # Disable AMP check that can fail on some GPU configs
        'workers': 0,  # Disable multiprocessing on Windows to avoid DLL loading issues
    }
    
    if args.resume:
        train_args['resume'] = True
    
    # Run training
    print("🚀 Starting GPU training...\n")
    results = model.train(**train_args)
    
    print("\n✓ Training completed!")
    print(f"Results saved to: {args.project}/{args.name}")
    
    # Save best model to models folder
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Find and copy best model
    best_model_path = Path(args.project) / args.name / 'weights' / 'best.pt'
    if best_model_path.exists():
        import shutil
        dest_path = Path(args.save_dir) / 'yolov8_atm_security_best.pt'
        shutil.copy(best_model_path, dest_path)
        print(f"✓ Best model saved to: {dest_path}")
        
        # Quick validation
        print("\n" + "="*60)
        print("Model validation on test set...")
        print("="*60)
        val_model = YOLO(str(dest_path))
        val_results = val_model.val(data=args.data, device=args.device)
        print(f"Validation mAP50: {val_results.box.map50:.3f}")
        print(f"Validation mAP50-95: {val_results.box.map:.3f}")
    else:
        print(f"⚠ Best model not found at: {best_model_path}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
