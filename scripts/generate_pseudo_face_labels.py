"""Generate pseudo YOLO labels for faces using OpenCV Haar cascade.

This creates `.txt` files with class 0 for detected faces for a subset of images.
Use this only as a bootstrap for quick testing — quality depends on detections.

Usage:
    python scripts/generate_pseudo_face_labels.py --src dataset --max-per-class 500
"""
import os
import argparse
import cv2


def is_image_file(name):
    return os.path.splitext(name)[1].lower() in ['.jpg', '.jpeg', '.png', '.bmp']


def write_yolo_label(txt_path, bbox, img_w, img_h, cls=0):
    # bbox: x, y, w, h in pixels (top-left x,y)
    x, y, w, h = bbox
    x_center = (x + w / 2) / img_w
    y_center = (y + h / 2) / img_h
    w_n = w / img_w
    h_n = h / img_h
    with open(txt_path, 'w') as f:
        f.write(f"{cls} {x_center:.6f} {y_center:.6f} {w_n:.6f} {h_n:.6f}\n")


def main(src='dataset', max_per_class=500):
    # Load Haar cascade for face
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    classes = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
    total = 0
    for cls in classes:
        cls_dir = os.path.join(src, cls)
        count = 0
        for root, _, files in os.walk(cls_dir):
            for f in files:
                if not is_image_file(f):
                    continue
                if count >= max_per_class:
                    break
                img_path = os.path.join(root, f)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                h, w = img.shape[:2]
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                if len(faces) == 0:
                    continue
                # pick largest face
                faces = sorted(faces, key=lambda b: b[2]*b[3], reverse=True)
                bbox = faces[0]
                txt_path = os.path.join(root, os.path.splitext(f)[0] + '.txt')
                write_yolo_label(txt_path, bbox, w, h, cls=0)
                count += 1
                total += 1
        print(f"Processed class '{cls}': wrote {count} pseudo-labels")

    print(f"Total pseudo-labels written: {total}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='dataset')
    parser.add_argument('--max-per-class', type=int, default=500)
    args = parser.parse_args()
    main(args.src, args.max_per_class)
