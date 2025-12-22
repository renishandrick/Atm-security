#!/usr/bin/env python3
"""Real-time training monitor - shows live progress."""

import os
import csv
import time
from pathlib import Path

def check_training_status():
    """Monitor training and show current status."""
    
    results_file = Path('runs/detect/atm_final/exp1/results.csv')
    weights_dir = Path('runs/detect/atm_final/exp1/weights')
    
    print("\n" + "="*70)
    print("ATM SECURITY TRAINING MONITOR")
    print("="*70)
    
    # Check if training has started
    if not results_file.exists():
        print("❌ Training not started yet OR wrong output folder")
        print(f"   Expected: {results_file}")
        return
    
    # Read CSV
    try:
        with open(results_file, 'r') as f:
            rows = list(csv.DictReader(f))
        
        if not rows:
            print("⏳ Training initializing... (no epochs completed yet)")
            return
        
        # Get last row (current epoch)
        current = rows[-1]
        epoch = current.get('Epoch', 'N/A')
        
        # Parse values
        try:
            epoch_num = int(float(epoch)) + 1
            box_loss = float(current.get('train/box_loss', 0))
            val_box_loss = float(current.get('val/box_loss', 0))
            mAP50 = float(current.get('metrics/mAP50', 0))
            gpu_mem = float(current.get('GPU_mem', 0))
        except:
            epoch_num = 'N/A'
            box_loss = val_box_loss = mAP50 = gpu_mem = 0
        
        # Check if training is complete
        best_exists = (weights_dir / 'best.pt').exists()
        last_exists = (weights_dir / 'last.pt').exists()
        
        print(f"\n📊 TRAINING PROGRESS")
        print(f"   Epoch: {epoch_num}/100")
        print(f"   Progress: {(epoch_num/100)*100:.1f}% complete")
        print(f"\n📈 METRICS")
        print(f"   Box Loss: {box_loss:.4f}")
        print(f"   Val Box Loss: {val_box_loss:.4f}")
        print(f"   mAP50: {mAP50:.4f}")
        print(f"   GPU Memory: {gpu_mem:.1f}GB")
        
        print(f"\n💾 MODEL FILES")
        print(f"   Last model saved: {'✅ Yes' if last_exists else '❌ No'}")
        print(f"   Best model saved: {'✅ Yes' if best_exists else '❌ No'}")
        
        # Estimate completion
        if epoch_num < 100:
            print(f"\n⏱️  STATUS: 🚀 TRAINING IN PROGRESS")
            print(f"   Epochs remaining: {100 - epoch_num}")
            print(f"   Estimated time: ~{(100-epoch_num) * 3} minutes remaining")
        else:
            print(f"\n✅ STATUS: TRAINING COMPLETED!")
            print(f"   Best model: runs/detect/atm_final/exp1/weights/best.pt")
            print(f"   Ready for inference!")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error reading training data: {e}")

def live_monitor(refresh_interval=30):
    """Continuously monitor training."""
    print("Live monitoring started. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            check_training_status()
            print(f"\nRefreshing in {refresh_interval} seconds... (Ctrl+C to stop)")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped.")

if __name__ == '__main__':
    import sys
    
    if '--live' in sys.argv:
        # Live monitoring mode (updates every 30 seconds)
        live_monitor()
    else:
        # One-time check
        check_training_status()
