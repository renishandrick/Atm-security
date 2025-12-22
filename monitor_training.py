#!/usr/bin/env python3
"""Monitor training progress in real-time."""

import csv
import time
from pathlib import Path
import os
import sys

def monitor_training(project_dir='runs/detect/atm_security/train_gpu5', poll_interval=30):
    """Monitor results.csv for training progress."""
    
    print("Training Monitor - ATM Security")
    print("=" * 70)
    print(f"Project: {project_dir}")
    print(f"Poll interval: {poll_interval} seconds\n")
    
    last_row = None
    errors = 0
    
    while True:
        try:
            # Find results.csv
            results_files = list(Path(project_dir).rglob('results.csv'))
            
            if not results_files:
                print(f"[WAIT] Waiting for training to start... (results.csv not found yet)")
                time.sleep(poll_interval)
                continue
            
            results_file = results_files[0]
            print(f"[INFO] Results file: {results_file}")
            
            # Read CSV
            try:
                with open(results_file, 'r') as f:
                    rows = list(csv.DictReader(f))
                
                if not rows:
                    print("[WAIT] Training initializing...")
                    time.sleep(poll_interval)
                    continue
                
                current_row = rows[-1]
                
                # Print header if first row
                if last_row is None and len(rows) == 1:
                    print("\n" + "-" * 70)
                    print(f"{'Epoch':<8} {'Loss/Box':<12} {'Loss/Cls':<12} {'Loss/Obj':<12} {'mAP50':<12}")
                    print("-" * 70)
                
                # Print progress
                if current_row != last_row:
                    epoch = current_row.get('epoch', 'N/A')
                    box_loss = current_row.get('train/box_loss', 'N/A')
                    cls_loss = current_row.get('train/cls_loss', 'N/A')
                    obj_loss = current_row.get('train/obj_loss', 'N/A')
                    mAP = current_row.get('metrics/mAP50', 'N/A')
                    
                    print(f"{epoch:<8} {box_loss:<12} {cls_loss:<12} {obj_loss:<12} {mAP:<12}")
                    last_row = current_row
                    errors = 0
                
                time.sleep(poll_interval)
            
            except Exception as e:
                errors += 1
                if errors > 5:
                    print(f"[ERR] Error reading {results_file}: {e}")
                    raise
                time.sleep(5)
        
        except KeyboardInterrupt:
            print("\n\n[DONE] Monitoring stopped")
            break
        except Exception as e:
            print(f"[ERR] Monitor error: {e}")
            break

if __name__ == '__main__':
    try:
        monitor_training()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
