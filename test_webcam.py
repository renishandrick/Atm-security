# test_webcam.py
from ultralytics import YOLO
import cv2

print("Loading model...")
model = YOLO('yolov8n.pt')

print("Opening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
    exit()

print("✅ Camera working! Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break
    
    results = model(frame, verbose=False)
    
    person_detected = False
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            if cls == 0:
                person_detected = True
                break
    
    status = "ACCESS GRANTED" if person_detected else "ACCESS DENIED"
    color = (0, 255, 0) if person_detected else (0, 0, 255)
    
    cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1, color, 2, cv2.LINE_AA)
    
    annotated_frame = results[0].plot()
    cv2.imshow("ATM Security - Press 'q' to quit", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Test completed!")