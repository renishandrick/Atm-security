#!/usr/bin/env python3
"""
Live training monitor - displays real-time training progress
Updates every 30 seconds
"""

import os
import time
import csv
from pathlib import Path
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_latest_epoch():
    """Read the latest epoch data from results.csv"""
    csv_path = Path('runs/detect/atm_security/train_gpu5/results.csv')
    
    if not csv_path.exists():
        return None
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                return rows[-1]
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return None

def format_time(seconds):
    """Format seconds into readable time"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def monitor_training():
    """Monitor training progress in real-time"""
    
    print("Starting live training monitor...")
    print("Press Ctrl+C to stop monitoring\n")
    time.sleep(2)
    
    start_time = time.time()
    last_epoch = None
    
    try:
        while True:
            clear_screen()
            
            # Header
            print("=" * 80)
            print("YOLOv8 TRAINING MONITOR - LIVE")
            print("=" * 80)
            print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Monitor Running: {format_time(time.time() - start_time)}")
            print("=" * 80)
            print()
            
            # Read latest epoch
            epoch_data = read_latest_epoch()
            
            if epoch_data:
                epoch = int(float(epoch_data.get('epoch', 0)))
                
                # Progress bar
                progress = (epoch / 100) * 100
                bar_length = 50
                filled = int(bar_length * epoch / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"PROGRESS: [{bar}] {epoch}/100 epochs ({progress:.1f}%)")
                print()
                
                # Training metrics
                print("TRAINING LOSSES:")
                print(f"  Box Loss:  {float(epoch_data.get('train/box_loss', 0)):.4f}")
                print(f"  Cls Loss:  {float(epoch_data.get('train/cls_loss', 0)):.4f}")
                print(f"  DFL Loss:  {float(epoch_data.get('train/dfl_loss', 0)):.4f}")
                print()
                
                # Validation metrics
                print("VALIDATION METRICS:")
                print(f"  Precision: {float(epoch_data.get('metrics/precision(B)', 0)):.4f}")
                print(f"  Recall:    {float(epoch_data.get('metrics/recall(B)', 0)):.4f}")
                print(f"  mAP50:     {float(epoch_data.get('metrics/mAP50(B)', 0)):.4f}")
                print(f"  mAP50-95:  {float(epoch_data.get('metrics/mAP50-95(B)', 0)):.4f}")
                print()
                
                # Time estimation
                if last_epoch is not None and epoch > last_epoch:
                    epochs_remaining = 100 - epoch
                    time_per_epoch = (time.time() - start_time) / (epoch - last_epoch)
                    eta_seconds = epochs_remaining * time_per_epoch
                    print(f"ESTIMATED TIME REMAINING: {format_time(eta_seconds)}")
                    print()
                
                last_epoch = epoch
                
                # Status
                if epoch >= 99:
                    print("STATUS: ✓ TRAINING COMPLETE!")
                else:
                    print(f"STATUS: → Training in progress (Epoch {epoch}/100)")
                
            else:
                print("STATUS: Waiting for training to start...")
                print("No results.csv found yet.")
            
            print()
            print("=" * 80)
            print("Next update in 30 seconds... (Press Ctrl+C to stop)")
            print("=" * 80)
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print("Training continues in the background.")

if __name__ == '__main__':
    monitor_training()
