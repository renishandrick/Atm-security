from ultralytics import YOLO
import sys

try:
    print("Resuming training from runs/detect/atm_security/train_gpu5/weights/last.pt")
    model = YOLO('runs/detect/atm_security/train_gpu5/weights/last.pt')
    model.train(resume=True)
except Exception as e:
    print(f"Error resuming: {e}")
    sys.exit(1)
