#!/usr/bin/env python3
"""Quick training status check"""
import csv
from pathlib import Path
from datetime import datetime

csv_path = Path('runs/detect/atm_security/train_gpu5/results.csv')

if csv_path.exists():
    with open(csv_path, 'r') as f:
        rows = list(csv.DictReader(f))
        if rows:
            last = rows[-1]
            epoch = int(float(last['epoch']))
            time_hours = float(last['time']) / 3600
            
            print("="*70)
            print("TRAINING STATUS - DETAILED UPDATE")
            print("="*70)
            print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last CSV Update: {datetime.fromtimestamp(csv_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print(f"LAST COMPLETED EPOCH: {epoch}/100 ({epoch}%)")
            print(f"Total Training Time: {time_hours:.2f} hours")
            print()
            print("TRAINING LOSSES:")
            print(f"  Box Loss:  {float(last['train/box_loss']):.4f}")
            print(f"  Cls Loss:  {float(last['train/cls_loss']):.4f}")
            print(f"  DFL Loss:  {float(last['train/dfl_loss']):.4f}")
            print()
            print("VALIDATION METRICS:")
            print(f"  Precision: {float(last['metrics/precision(B)']):.4f}")
            print(f"  Recall:    {float(last['metrics/recall(B)']):.4f}")
            print(f"  mAP50:     {float(last['metrics/mAP50(B)']):.4f}")
            print(f"  mAP50-95:  {float(last['metrics/mAP50-95(B)']):.4f}")
            print()
            
            # Calculate ETA
            epochs_done = epoch
            epochs_remaining = 100 - epoch
            avg_time_per_epoch = time_hours / epochs_done if epochs_done > 0 else 0
            eta_hours = epochs_remaining * avg_time_per_epoch
            
            print(f"ESTIMATED TIME REMAINING: {eta_hours:.1f} hours ({eta_hours*60:.0f} minutes)")
            print()
            
            if epoch >= 99:
                print("STATUS: ✓ TRAINING COMPLETE!")
            else:
                print(f"STATUS: → Training in progress")
                print(f"NOTE: Currently working on epoch {epoch+1}, will update CSV when complete")
            
            print("="*70)
else:
    print("No results.csv found")
