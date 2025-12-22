# atm_security_final.py
from ultralytics import YOLO
import cv2
import time
import os
import argparse


class ATMSecuritySystem:
    def __init__(self, model_path):
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(0)

        # Wait for camera
        time.sleep(1)
        if not self.cap.isOpened():
            print("❌ ERROR: Cannot open camera!")
            exit(1)

        print("✅ ATM Security System Ready!")

    def check_access(self, detections):
        """Determine access by mapping detected classes to (face, mask, helmet).

        This is robust to different model label sets: if the loaded model provides
        `model.names` (class name mapping), we try to map COCO/class names to the
        project's expected classes. Otherwise we fall back to numeric indices.
        """
        has_face = False
        has_obstruction = False

        # Try to infer class name mapping if available
        model_names = None
        try:
            model_names = self.model.model.names if hasattr(self.model, 'model') and hasattr(self.model.model, 'names') else None
        except Exception:
            model_names = None

        for box in detections.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if conf <= 0.6:
                continue

            # If model_names available, map by name
            if model_names:
                name = model_names.get(cls, str(cls)).lower()
                if 'person' in name or 'face' in name:
                    has_face = True
                if 'mask' in name or 'helmet' in name or 'hardhat' in name or 'hat' in name:
                    has_obstruction = True
            else:
                # Fall back to numeric indices expected by your custom dataset
                if cls == 0:
                    has_face = True
                elif cls == 1 or cls == 2:
                    has_obstruction = True

        return has_face and not has_obstruction

    def run(self):
        print("🔴 Live detection started...")
        print("Press 'q' to quit")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break

            results = self.model(frame, verbose=False)

            if len(results) > 0:
                access_granted = self.check_access(results[0])

                status = "ACCESS GRANTED" if access_granted else "ACCESS DENIED"
                color = (0, 255, 0) if access_granted else (0, 0, 255)

                # Draw status
                cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                           1.5, color, 3, cv2.LINE_AA)

                if not access_granted:
                    cv2.putText(frame, "Remove Mask/Helmet", (50, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            annotated_frame = results[0].plot() if len(results) > 0 else frame
            cv2.imshow("ATM Security System - Camera", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ System shut down")


def find_model(user_path=None):
    # prefer user path if provided, then trained weights, then fallback to yolov8n
    if user_path and os.path.exists(user_path):
        return user_path

    trained = os.path.join('runs', 'detect', 'train', 'weights', 'best.pt')
    if os.path.exists(trained):
        return trained

    # fallback to bundled pretrained if available
    if os.path.exists('yolov8n.pt'):
        return 'yolov8n.pt'

    # final fallback: let Ultralytics download the default model by passing 'yolov8n'
    return 'yolov8n'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Path to model file (pt) or model name', default=None)
    args = parser.parse_args()

    model_path = find_model(args.model)
    print(f"Using model: {model_path}")

    system = ATMSecuritySystem(model_path)
    system.run()