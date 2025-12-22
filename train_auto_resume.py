#!/usr/bin/env python3
"""
Auto-resume training script with crash recovery.
Monitors training and automatically resumes if it stops.
"""

import os
import sys
import time
from pathlib import Path
from ultralytics import YOLO

def get_latest_checkpoint():
    """Find the latest checkpoint to resume from."""
    checkpoint = Path('runs/detect/atm_security/train_gpu5/weights/last.pt')
    if checkpoint.exists():
        return str(checkpoint)
    return None

def train_with_auto_resume(max_retries=5):
    """Train with automatic resume on failure."""
    
    checkpoint = get_latest_checkpoint()
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"\n{'='*70}")
            print(f"Training Attempt {retry_count + 1}/{max_retries}")
            print(f"{'='*70}\n")
            
            if checkpoint and os.path.exists(checkpoint):
                print(f"Resuming from checkpoint: {checkpoint}")
                model = YOLO(checkpoint)
                results = model.train(resume=True)
            else:
                print("Starting fresh training...")
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
                    amp=False
                )
            
            print("\n✓ Training completed successfully!")
            return 0
            
        except KeyboardInterrupt:
            print("\n\nTraining interrupted by user.")
            return 1
            
        except Exception as e:
            retry_count += 1
            print(f"\n❌ Training failed: {e}")
            
            if retry_count < max_retries:
                wait_time = 30
                print(f"Waiting {wait_time} seconds before retry {retry_count + 1}...")
                time.sleep(wait_time)
                
                # Update checkpoint path
                checkpoint = get_latest_checkpoint()
            else:
                print(f"\n❌ Max retries ({max_retries}) reached. Exiting.")
                return 1
    
    return 1

if __name__ == '__main__':
    exit_code = train_with_auto_resume()
    sys.exit(exit_code)
