#!/usr/bin/env python3
"""
Web server for training dashboard
Provides real-time training data via HTTP API
"""

import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class TrainingDataProvider:
    """Provides training data from CSV and system stats"""
    
    def __init__(self):
        self.csv_path = Path('runs/detect/atm_security/train_gpu5/results.csv')
    
    def get_gpu_stats(self):
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
                    'memory': f"{parts[1].strip()} MB / {parts[2].strip()} MB",
                    'temperature': parts[3].strip(),
                    'power': parts[4].strip()
                }
        except Exception as e:
            print(f"Error getting GPU stats: {e}")
        return None
    
    def is_training_running(self):
        """Check if Python training process is running"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True,
                timeout=5
            )
            count = result.stdout.count('python.exe')
            return count >= 3
        except:
            return False
    
    def get_training_status(self):
        """Get latest training metrics from CSV"""
        if not self.csv_path.exists():
            return None
        
        try:
            with open(self.csv_path, 'r') as f:
                rows = list(csv.DictReader(f))
                if rows:
                    last = rows[-1]
                    epoch = int(float(last['epoch']))
                    time_hours = float(last['time']) / 3600
                    
                    # Calculate ETA
                    avg_time_per_epoch = time_hours / epoch if epoch > 0 else 0
                    epochs_remaining = 100 - epoch
                    eta_hours = epochs_remaining * avg_time_per_epoch
                    eta_minutes = eta_hours * 60
                    
                    # Calculate completion time
                    completion_timestamp = datetime.now().timestamp() + (eta_hours * 3600)
                    completion_dt = datetime.fromtimestamp(completion_timestamp)
                    
                    return {
                        'epoch': epoch,
                        'time_hours': time_hours,
                        'box_loss': float(last['train/box_loss']),
                        'cls_loss': float(last['train/cls_loss']),
                        'dfl_loss': float(last['train/dfl_loss']),
                        'precision': float(last['metrics/precision(B)']),
                        'recall': float(last['metrics/recall(B)']),
                        'map50': float(last['metrics/mAP50(B)']),
                        'map50_95': float(last['metrics/mAP50-95(B)']),
                        'time_elapsed': f"{time_hours:.2f} hours",
                        'avg_per_epoch': f"{avg_time_per_epoch*60:.1f} min",
                        'time_remaining': f"{eta_hours:.1f} hours ({eta_minutes:.0f} min)",
                        'completion_time': completion_dt.strftime('%I:%M %p')
                    }
        except Exception as e:
            print(f"Error reading training status: {e}")
        
        return None
    
    def get_all_data(self):
        """Get all training data"""
        return {
            'is_running': self.is_training_running(),
            'gpu': self.get_gpu_stats(),
            'training': self.get_training_status(),
            'timestamp': datetime.now().isoformat()
        }

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    data_provider = TrainingDataProvider()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            # Return JSON data
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = self.data_provider.get_all_data()
            self.wfile.write(json.dumps(data).encode())
            
        elif self.path == '/' or self.path == '/index.html':
            # Serve dashboard HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_path = Path('training_dashboard.html')
            if html_path.exists():
                with open(html_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b'<h1>Dashboard HTML not found</h1>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def run_server(port=8000):
    """Run the dashboard server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print("=" * 70)
    print("TRAINING DASHBOARD SERVER")
    print("=" * 70)
    print(f"\nServer running on http://localhost:{port}")
    print(f"\nOpen your browser and go to:")
    print(f"  http://localhost:{port}")
    print(f"\nThe dashboard will auto-refresh every 5 seconds")
    print(f"\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
