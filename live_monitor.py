#!/usr/bin/env python3
"""
Real-time Training Monitor with Auto-Refresh
Shows live updates every 10 seconds
"""

import os
import sys
import csv
import time
import subprocess
from pathlib import Path
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_gpu_stats():
    """Get current GPU statistics"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw',
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(',')
            return {
                'utilization': parts[0].strip(),
                'memory_used': parts[1].strip(),
                'memory_total': parts[2].strip(),
                'temperature': parts[3].strip(),
                'power': parts[4].strip()
            }
    except:
        pass
    return None

def get_training_status():
    """Get latest training metrics from CSV"""
    csv_path = Path('runs/detect/atm_security/train_gpu5/results.csv')
    
    if not csv_path.exists():
        return None
    
    try:
        with open(csv_path, 'r') as f:
            rows = list(csv.DictReader(f))
            if rows:
                last = rows[-1]
                csv_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
                return {
                    'epoch': int(float(last['epoch'])),
                    'time_hours': float(last['time']) / 3600,
                    'box_loss': float(last['train/box_loss']),
                    'cls_loss': float(last['train/cls_loss']),
                    'dfl_loss': float(last['train/dfl_loss']),
                    'precision': float(last['metrics/precision(B)']),
                    'recall': float(last['metrics/recall(B)']),
                    'map50': float(last['metrics/mAP50(B)']),
                    'map50_95': float(last['metrics/mAP50-95(B)']),
                    'csv_update_time': csv_time
                }
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return None

def is_training_running():
    """Check if Python training process is running"""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Count python processes (more than 2 usually means training is active)
        count = result.stdout.count('python.exe')
        return count >= 3
    except:
        return False

def create_progress_bar(current, total, length=50):
    """Create a visual progress bar"""
    filled = int(length * current / total)
    bar = '=' * filled + '-' * (length - filled)
    percent = (current / total) * 100
    return f"[{bar}] {current}/{total} ({percent:.1f}%)"

def monitor_live():
    """Main monitoring loop"""
    
    print("Starting live training monitor...")
    print("Updates every 10 seconds. Press Ctrl+C to stop.\n")
    time.sleep(2)
    
    start_time = time.time()
    last_epoch = None
    
    try:
        while True:
            clear_screen()
            
            now = datetime.now()
            
            # Header
            print("=" * 80)
            print(" " * 20 + "YOLOV8 TRAINING - LIVE MONITOR")
            print("=" * 80)
            print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Monitor Uptime: {int(time.time() - start_time)} seconds")
            print("=" * 80)
            print()
            
            # Check if training is running
            is_running = is_training_running()
            
            if is_running:
                print("TRAINING STATUS: [ACTIVE] Python processes detected")
            else:
                print("TRAINING STATUS: [NOT RUNNING] No Python processes found")
            print()
            
            # GPU Stats
            gpu = get_gpu_stats()
            if gpu:
                print("GPU STATUS:")
                print(f"  Utilization:  {gpu['utilization']}%")
                print(f"  VRAM Usage:   {gpu['memory_used']} MB / {gpu['memory_total']} MB")
                print(f"  Temperature:  {gpu['temperature']}°C")
                print(f"  Power Draw:   {gpu['power']} W")
                
                # Temperature warning
                temp = float(gpu['temperature'])
                if temp > 80:
                    print("  WARNING: High temperature!")
                elif temp > 75:
                    print("  NOTICE: Temperature elevated")
                else:
                    print("  Status: Temperature normal")
            else:
                print("GPU STATUS: Unable to read GPU stats")
            
            print()
            print("-" * 80)
            print()
            
            # Training Progress
            status = get_training_status()
            
            if status:
                epoch = status['epoch']
                
                # Progress bar
                print("TRAINING PROGRESS:")
                print(create_progress_bar(epoch, 100, 60))
                print()
                
                # Time info
                time_elapsed = status['time_hours']
                avg_time_per_epoch = time_elapsed / epoch if epoch > 0 else 0
                epochs_remaining = 100 - epoch
                eta_hours = epochs_remaining * avg_time_per_epoch
                eta_minutes = eta_hours * 60
                
                print(f"Current Epoch:        {epoch}/100")
                print(f"Time Elapsed:         {time_elapsed:.2f} hours")
                print(f"Avg Time/Epoch:       {avg_time_per_epoch*60:.1f} minutes")
                print(f"Estimated Remaining:  {eta_hours:.1f} hours ({eta_minutes:.0f} minutes)")
                
                if eta_hours > 0:
                    completion_time = datetime.now().timestamp() + (eta_hours * 3600)
                    completion_dt = datetime.fromtimestamp(completion_time)
                    print(f"Expected Completion:  {completion_dt.strftime('%Y-%m-%d %I:%M %p')}")
                
                print()
                print("-" * 80)
                print()
                
                # Losses
                print("TRAINING LOSSES:")
                print(f"  Box Loss:  {status['box_loss']:.4f}")
                print(f"  Cls Loss:  {status['cls_loss']:.4f}")
                print(f"  DFL Loss:  {status['dfl_loss']:.4f}")
                print()
                
                # Metrics
                print("VALIDATION METRICS:")
                print(f"  Precision: {status['precision']:.4f}")
                print(f"  Recall:    {status['recall']:.4f}")
                print(f"  mAP50:     {status['map50']:.4f}")
                print(f"  mAP50-95:  {status['map50_95']:.4f}")
                
                if status['map50'] == 0:
                    print("  Note: Metrics will become non-zero around epoch 30-50")
                
                print()
                print("-" * 80)
                print()
                
                # CSV update info
                csv_age = (now - status['csv_update_time']).total_seconds()
                csv_age_min = csv_age / 60
                
                print(f"Last CSV Update: {status['csv_update_time'].strftime('%H:%M:%S')} ({csv_age_min:.1f} min ago)")
                
                if csv_age_min > 15:
                    print(f"  Currently processing epoch {epoch + 1}...")
                    print(f"  CSV will update when epoch completes (~7-10 min per epoch)")
                else:
                    print(f"  Recent update - epoch {epoch} just completed!")
                
                # Track epoch changes
                if last_epoch is not None and epoch > last_epoch:
                    print(f"\n  >>> NEW EPOCH COMPLETED! ({last_epoch} -> {epoch})")
                
                last_epoch = epoch
                
            else:
                print("TRAINING DATA: No results.csv found yet")
                print("Training may be initializing...")
            
            print()
            print("=" * 80)
            print("Next update in 10 seconds... (Press Ctrl+C to stop)")
            print("=" * 80)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("Monitoring stopped by user.")
        print("Training continues in the background.")
        print("=" * 80)

if __name__ == '__main__':
    monitor_live()
