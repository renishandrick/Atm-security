#!/usr/bin/env python3
"""
Simple Training Monitor - Shows current epoch progress
Refreshes every 10 seconds
"""

import os
import csv
import time
from pathlib import Path
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_training():
    """Monitor the current training run"""
    
    # Find the most recent training directory
    results_file = Path('runs/detect/atm_security/nano_fast3/results.csv')
    
    if not results_file.exists():
        print("Training has not started yet or results.csv not found.")
        print(f"Looking for: {results_file}")
        return
    
    while True:
        try:
            clear_screen()
            
            print("=" * 80)
            print("YOLOV8 NANO TRAINING MONITOR")
            print("=" * 80)
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Location: {results_file.parent}")
            print("=" * 80)
            print()
            
            # Read the results CSV
            with open(results_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                print("Training started but no epochs completed yet...")
                print("Waiting for first epoch to complete...")
            else:
                # Get the last completed epoch
                last_row = rows[-1]
                total_epochs = 100
                
                # Parse epoch number
                try:
                    current_epoch = int(float(last_row.get('epoch', 0))) + 1
                except:
                    current_epoch = len(rows)
                
                # Calculate progress
                progress_pct = (current_epoch / total_epochs) * 100
                
                # Display current status
                print(f"CURRENT EPOCH: {current_epoch}/{total_epochs}")
                print(f"PROGRESS: {progress_pct:.1f}%")
                print()
                
                # Progress bar
                bar_length = 50
                filled = int(bar_length * current_epoch / total_epochs)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"[{bar}] {current_epoch}/{total_epochs}")
                print()
                
                # Show latest metrics
                print("LATEST METRICS:")
                print("-" * 80)
                
                try:
                    box_loss = float(last_row.get('train/box_loss', 0))
                    cls_loss = float(last_row.get('train/cls_loss', 0))
                    dfl_loss = float(last_row.get('train/dfl_loss', 0))
                    
                    # Get column names that contain mAP
                    mAP50_key = [k for k in last_row.keys() if 'mAP50' in k and 'mAP50-95' not in k]
                    mAP50 = float(last_row.get(mAP50_key[0], 0)) if mAP50_key else 0
                    
                    precision_key = [k for k in last_row.keys() if 'precision' in k]
                    precision = float(last_row.get(precision_key[0], 0)) if precision_key else 0
                    
                    recall_key = [k for k in last_row.keys() if 'recall' in k]
                    recall = float(last_row.get(recall_key[0], 0)) if recall_key else 0
                    
                    print(f"  Box Loss:     {box_loss:.4f}")
                    print(f"  Class Loss:   {cls_loss:.4f}")
                    print(f"  DFL Loss:     {dfl_loss:.4f}")
                    print(f"  mAP50:        {mAP50:.4f}")
                    print(f"  Precision:    {precision:.4f}")
                    print(f"  Recall:       {recall:.4f}")
                except Exception as e:
                    print(f"  Error reading metrics: {e}")
                
                print()
                print("-" * 80)
                
                # Estimate time remaining
                if current_epoch > 0:
                    # Assume ~4-5 minutes per epoch
                    avg_time_per_epoch = 4.5  # minutes
                    remaining_epochs = total_epochs - current_epoch
                    estimated_minutes = remaining_epochs * avg_time_per_epoch
                    estimated_hours = estimated_minutes / 60
                    
                    print(f"ESTIMATED TIME REMAINING: {estimated_hours:.1f} hours ({estimated_minutes:.0f} minutes)")
                    print(f"Epochs remaining: {remaining_epochs}")
                
                print()
                print("=" * 80)
                
                # Show recent progress (last 5 epochs)
                if len(rows) >= 5:
                    print()
                    print("RECENT PROGRESS (Last 5 Epochs):")
                    print("-" * 80)
                    print(f"{'Epoch':<8} {'Box Loss':<12} {'Class Loss':<12} {'mAP50':<10}")
                    print("-" * 80)
                    
                    for row in rows[-5:]:
                        try:
                            epoch = int(float(row.get('epoch', 0))) + 1
                            box = float(row.get('train/box_loss', 0))
                            cls = float(row.get('train/cls_loss', 0))
                            
                            mAP50_key = [k for k in row.keys() if 'mAP50' in k and 'mAP50-95' not in k]
                            mAP = float(row.get(mAP50_key[0], 0)) if mAP50_key else 0
                            
                            print(f"{epoch:<8} {box:<12.4f} {cls:<12.4f} {mAP:<10.4f}")
                        except:
                            pass
                    
                    print("-" * 80)
            
            print()
            print("Refreshing in 10 seconds... (Press Ctrl+C to stop)")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == '__main__':
    print("Starting training monitor...")
    print("Looking for: runs/detect/atm_security/nano_fast3/results.csv")
    print()
    time.sleep(2)
    monitor_training()
