#!/usr/bin/env python3
"""Simple GPU training script for ATM Security YOLOv8."""

import sys
from pathlib import Path
from ultralytics import YOLO

# Configuration
WEIGHTS = 'yolov8m.pt'
DATA_CONFIG = 'data.yaml'
EPOCHS = 100
BATCH_SIZE = 32
IMG_SIZE = 640
DEVICE = 0  # GPU device
PROJECT = 'runs/detect/atm_security_final'
EXPERIMENT_NAME = 'train_100epochs'

def main():
    print("="*60)
    print("ATM Security YOLOv8 GPU Training")
    print("="*60)
    print(f"Weights: {WEIGHTS}")
    print(f"Data: {DATA_CONFIG}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch: {BATCH_SIZE}")
    print(f"Device: {DEVICE} (GPU)")
    print(f"Output: {PROJECT}/{EXPERIMENT_NAME}")
    print("="*60)
    
    # Verify data config exists
    if not Path(DATA_CONFIG).exists():
        print(f"❌ Error: {DATA_CONFIG} not found")
        return 1
    
    # Load model
    print("\nLoading model...")
    model = YOLO(WEIGHTS)
    
    # Train
    print("\n🚀 Starting training...\n")
    try:
        results = model.train(
            data=DATA_CONFIG,
            epochs=EPOCHS,
            batch=BATCH_SIZE,
            imgsz=IMG_SIZE,
            device=DEVICE,
            project=PROJECT,
            name=EXPERIMENT_NAME,
            save=True,
            patience=20,
            verbose=True,
            amp=False,  # Disable AMP to avoid compatibility issues
            val=True,   # Enable validation
            plots=True, # Generate plots
        )
        
        print("\n✓ Training completed!")
        
        # Find best model
        best_model_path = Path(PROJECT) / EXPERIMENT_NAME / 'weights' / 'best.pt'
        if best_model_path.exists():
            import shutil
            Path('models').mkdir(exist_ok=True)
            dest = Path('models') / 'yolov8_atm_security_best.pt'
            shutil.copy(best_model_path, dest)
            print(f"✓ Best model saved to: {dest}")
            return 0
        else:
            print(f"⚠ Best model not found at: {best_model_path}")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
