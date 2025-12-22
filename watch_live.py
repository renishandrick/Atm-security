#!/usr/bin/env python3
"""
Live Training Watcher - Shows real-time progress
Works even during first epoch!
"""

import os
import csv
import time
from pathlib import Path
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def watch_live():
    """Watch training with live updates"""
    
    results_file = Path('runs/detect/atm_security/nano_fast3/results.csv')
    
    print("=" * 80)
    print("LIVE TRAINING MONITOR")
    print("=" * 80)
    print()
    print("Monitoring: runs/detect/atm_security/nano_fast3/")
    print("Press Ctrl+C to stop")
    print()
    print("=" * 80)
    
    last_epoch = 0
    
    while True:
        try:
            clear_screen()
            
            print("=" * 80)
            print(f"YOLOV8 NANO TRAINING - LIVE MONITOR")
            print("=" * 80)
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 80)
            print()
            
            if not results_file.exists():
                print("STATUS: First epoch in progress...")
                print()
                print("Waiting for epoch 1 to complete (~4-5 minutes)")
                print()
                print("What's happening:")
                print("  ✓ Model loaded")
                print("  ✓ Dataset scanned (6,444 train + 1,576 val images)")
                print("  ✓ GPU training started")
                print("  ⏳ Processing 327 batches...")
                print()
                print("The results.csv file will appear when epoch 1 finishes.")
                
            else:
                # Read results
                with open(results_file, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                if rows:
                    last_row = rows[-1]
                    current_epoch = len(rows)
                    
                    # Check if new epoch completed
                    if current_epoch > last_epoch:
                        print(f"🎉 NEW EPOCH COMPLETED! Epoch {current_epoch}")
                        print()
                        last_epoch = current_epoch
                    
                    # Progress
                    progress = (current_epoch / 100) * 100
                    bar_len = 50
                    filled = int(bar_len * current_epoch / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    
                    print(f"EPOCH: {current_epoch}/100 ({progress:.1f}%)")
                    print(f"[{bar}]")
                    print()
                    
                    # Latest metrics
                    print("LATEST METRICS (Epoch {})".format(current_epoch))
                    print("-" * 80)
                    
                    try:
                        # Get all column names
                        cols = list(last_row.keys())
                        
                        # Find metric columns
                        box_loss = float(last_row.get('train/box_loss', 0))
                        cls_loss = float(last_row.get('train/cls_loss', 0))
                        dfl_loss = float(last_row.get('train/dfl_loss', 0))
                        
                        # Find mAP column
                        map_col = [c for c in cols if 'mAP50' in c and 'mAP50-95' not in c]
                        mAP50 = float(last_row.get(map_col[0], 0)) if map_col else 0
                        
                        # Find precision/recall
                        prec_col = [c for c in cols if 'precision' in c]
                        rec_col = [c for c in cols if 'recall' in c]
                        
                        precision = float(last_row.get(prec_col[0], 0)) if prec_col else 0
                        recall = float(last_row.get(rec_col[0], 0)) if rec_col else 0
                        
                        print(f"  Training Loss:")
                        print(f"    Box Loss:   {box_loss:.4f}")
                        print(f"    Class Loss: {cls_loss:.4f}")
                        print(f"    DFL Loss:   {dfl_loss:.4f}")
                        print()
                        print(f"  Validation Metrics:")
                        print(f"    mAP50:      {mAP50:.4f} {'✓ Detecting!' if mAP50 > 0.1 else '(learning...)'}")
                        print(f"    Precision:  {precision:.4f}")
                        print(f"    Recall:     {recall:.4f}")
                        
                    except Exception as e:
                        print(f"  (Parsing metrics: {e})")
                    
                    print()
                    print("-" * 80)
                    
                    # Time estimate
                    remaining = 100 - current_epoch
                    est_minutes = remaining * 4  # ~4 min per epoch
                    est_hours = est_minutes / 60
                    
                    print()
                    print(f"TIME ESTIMATE:")
                    print(f"  Epochs remaining: {remaining}")
                    print(f"  Estimated time:   {est_hours:.1f} hours ({est_minutes:.0f} minutes)")
                    
                    # Show trend if we have multiple epochs
                    if len(rows) >= 3:
                        print()
                        print("RECENT PROGRESS:")
                        print("-" * 80)
                        print(f"{'Epoch':<8} {'Box Loss':<12} {'Class Loss':<12} {'mAP50':<10}")
                        print("-" * 80)
                        
                        for row in rows[-5:]:
                            try:
                                ep = rows.index(row) + 1
                                box = float(row.get('train/box_loss', 0))
                                cls = float(row.get('train/cls_loss', 0))
                                
                                map_col = [c for c in row.keys() if 'mAP50' in c and 'mAP50-95' not in c]
                                map_val = float(row.get(map_col[0], 0)) if map_col else 0
                                
                                print(f"{ep:<8} {box:<12.4f} {cls:<12.4f} {map_val:<10.4f}")
                            except:
                                pass
                        print("-" * 80)
            
            print()
            print("=" * 80)
            print("Refreshing in 5 seconds... (Ctrl+C to stop)")
            print("=" * 80)
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped.")
            print("\nTraining is still running in the background!")
            print("Run this script again anytime to check progress.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    watch_live()
