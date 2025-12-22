# test_ultralytics.py
try:
    from ultralytics import YOLO
    print("✅ Ultralytics installed successfully!")
except ImportError as e:
    print(f"❌ Ultralytics not installed: {e}")