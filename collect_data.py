# collect_data.py
import cv2
import os
import time

# Create directories
os.makedirs('dataset/face', exist_ok=True)
os.makedirs('dataset/mask', exist_ok=True) 
os.makedirs('dataset/helmet', exist_ok=True)

cap = cv2.VideoCapture(0)

print("=== DATA COLLECTION ===")
print("1 - Clear Face (no covering)")
print("2 - Face with Mask")
print("3 - Face with Helmet") 
print("q - Quit and Finish")

counter = {'face': 0, 'mask': 0, 'helmet': 0}

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Show instructions on screen
    cv2.putText(frame, "1:Face  2:Mask  3:Helmet  q:Quit", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Face: {counter['face']}  Mask: {counter['mask']}  Helmet: {counter['helmet']}", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    cv2.imshow("Data Collection - Use YOUR Webcam", frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('1'):
        filename = f'dataset/face/face_{counter["face"]:04d}.jpg'
        cv2.imwrite(filename, frame)
        counter['face'] += 1
        print(f"✅ Saved: {filename}")
        time.sleep(0.5)  # Small delay
        
    elif key == ord('2'):
        filename = f'dataset/mask/mask_{counter["mask"]:04d}.jpg'
        cv2.imwrite(filename, frame)
        counter['mask'] += 1
        print(f"✅ Saved: {filename}")
        time.sleep(0.5)
        
    elif key == ord('3'):
        filename = f'dataset/helmet/helmet_{counter["helmet"]:04d}.jpg'
        cv2.imwrite(filename, frame)
        counter['helmet'] += 1
        print(f"✅ Saved: {filename}")
        time.sleep(0.5)
        
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"🎉 Collection Complete!")
print(f"📊 Total images: Face={counter['face']}, Mask={counter['mask']}, Helmet={counter['helmet']}")
