# test_opencv.py
import cv2

print("Testing OpenCV...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ OpenCV installed and camera works!")
    cap.release()
else:
    print("❌ Camera issue")