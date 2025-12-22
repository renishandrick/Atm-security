#!/usr/bin/env python3
"""Quick training status check."""

from pathlib import Path
import time

def check_status():
    base = Path('runs/detect/atm_final/nano_model')
    results = base / 'results.csv'
    best_model = base / 'weights' / 'best.pt'
    
    print("\n" + "="*60)
    print("TRAINING STATUS")
    print("="*60)
    
    # Check for best model
    if best_model.exists():
        size_mb = best_model.stat().st_size / (1024*1024)
        print(f"\n✅ TRAINING COMPLETE!")
        print(f"   Best model: {best_model}")
        print(f"   Size: {size_mb:.1f} MB")
        return
    
    # Check for results
    if results.exists():
        with open(results) as f:
            lines = f.readlines()
        
        if len(lines) > 1:  # Has data
            last_line = lines[-1].strip().split(',')
            try:
                epoch = last_line[0]
                print(f"\n🚀 STILL TRAINING")
                print(f"   Epochs completed: {epoch}/50")
                print(f"   Progress: {float(epoch)/50*100:.1f}%")
            except:
                print("\n⏳ Training in progress...")
        else:
            print("\n⏳ Training starting (initializing)...")
    else:
        # Check if training folder exists
        if base.exists():
            # Count files in weights folder to see if anything is being created
            weights_dir = base / 'weights'
            if weights_dir.exists():
                files = list(weights_dir.glob('*'))
                print(f"\n⏳ Training initializing...")
                print(f"   Files in weights: {len(files)}")
            else:
                print("\n⏳ Training folder created, waiting for first checkpoint...")
        else:
            print("\n❌ Training folder not found!")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    check_status()
