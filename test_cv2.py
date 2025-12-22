# test_cv2.py
try:
    import cv2
    print(f"✅ OpenCV installed! Version: {cv2.__version__}")
    
    # Test camera
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ Camera works!")
        cap.release()
    else:
        print("⚠️  Camera not accessible")
        
except Exception as e:
    print(f"❌ OpenCV error: {e}")