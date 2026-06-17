#!/usr/bin/env python3
"""
Inference script for ATM Security model (face, mask, helmet detection).
Runs on a single image or webcam.
"""

import argparse
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

def run_on_image(model, image_path, conf=0.5, save_path=None):
    """Run inference on a single image."""
    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    print("Running inference...")
    results = model(image, conf=conf, verbose=False)
    result = results[0]
    
    # Visualize
    annotated_frame = result.plot()
    
    # Display stats
    detections = result.boxes
    print(f"\nDetections ({len(detections)} total):")
    for box, conf, cls in zip(detections.xyxy, detections.conf, detections.cls):
        class_name = model.names[int(cls)]
        print(f"  {class_name}: {float(conf):.2%}")
    
    # Save if requested
    if save_path:
        cv2.imwrite(save_path, annotated_frame)
        print(f"✓ Saved to: {save_path}")
    
    # Display
    cv2.imshow("ATM Security Detection", annotated_frame)
    print("Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_on_webcam(model, conf=0.5):
    """Run inference on webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return
    
    print("Webcam stream started (press 'q' to quit)")
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run inference every 3 frames (for performance)
        if frame_count % 3 == 0:
            # OPTIMIZATION: Resize frame for faster inference
            h, w = frame.shape[:2]
            if w > 640:
                scale = 640 / w
                frame_small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            else:
                frame_small = frame
                
            results = model(frame_small, conf=conf, verbose=False)
            result = results[0]
            frame = result.plot() # result.plot() returns the image at the size of the input (small)
            
            # Upscale back for display if it was resized
            if w > 640:
                frame = cv2.resize(frame, (w, h))
            
            # Check for mask (1) or helmet (2)
            classes = result.boxes.cls.tolist()
            instructions = []
            if 1 in classes:
                instructions.append("PLEASE REMOVE MASK")
            if 2 in classes:
                instructions.append("PLEASE REMOVE HELMET")
            
            # Add instruction overlay if needed
            if instructions:
                h, w, _ = frame.shape
                # Draw a prominent red banner at the top
                overlay_height = 60 * len(instructions)
                cv2.rectangle(frame, (0, 0), (w, overlay_height), (0, 0, 255), -1)
                
                for i, msg in enumerate(instructions):
                    cv2.putText(frame, msg, (20, 45 + (i * 50)), 
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)
        
        cv2.imshow("ATM Security Detection - Webcam", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames")

def main():
    parser = argparse.ArgumentParser(description='ATM Security Detection Inference')
    parser.add_argument('--model', default='models/yolov8_atm_security_best.pt',
                       help='Path to trained model weights')
    parser.add_argument('--image', help='Path to input image')
    parser.add_argument('--webcam', action='store_true', help='Use webcam')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--device', default='cuda', help='GPU device or cpu')
    parser.add_argument('--output', help='Path to save output image')
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"Error: Model not found at {args.model}")
        print(f"Available models in ./models/:")
        import os
        models_dir = Path('models')
        if models_dir.exists():
            for f in models_dir.glob('*.pt'):
                print(f"  - {f}")
        return 1
    
    print(f"Loading model: {args.model}")
    model = YOLO(args.model)
    model.to(args.device)
    print(f"✓ Model loaded")
    print(f"  Classes: {model.names}")
    
    if args.image:
        run_on_image(model, args.image, args.conf, args.output)
    elif args.webcam:
        run_on_webcam(model, args.conf)
    else:
        print("Please specify --image or --webcam")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
