"""Pseudo-label pipeline

Scans `--images` (expects `train` and `val`), and for any image missing a YOLO `.txt`
in the `--labels_out` corresponding location, runs a face Haar detector and writes
one YOLO bbox (largest face) as class 0. Does NOT overwrite existing labels.

Usage:
  python scripts/pseudo_label_pipeline.py --images dataset/images --labels-out dataset/labels --max-per-split 100000
"""

import argparse
from pathlib import Path
import cv2


def is_image(p: Path):
    return p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}


def write_yolo(txt_path: Path, cls: int, bbox, w, h):
    x, y, bw, bh = bbox
    x_center = (x + bw / 2.0) / w
    y_center = (y + bh / 2.0) / h
    w_n = bw / w
    h_n = bh / h
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(txt_path, 'w') as f:
        f.write(f"{cls} {x_center:.6f} {y_center:.6f} {w_n:.6f} {h_n:.6f}\n")


def process_split(images_root: Path, labels_out: Path, split: str, face_cascade, max_per_split: int):
    img_dir = images_root / split
    if not img_dir.exists():
        return 0, 0
    imgs = [p for p in img_dir.rglob('*') if p.is_file() and is_image(p)]
    wrote = 0
    seen = 0
    for img in imgs:
        # relative path inside split
        rel = img.relative_to(images_root)
        # corresponding label path under labels_out
        lbl_path = labels_out / rel.parent / (img.stem + '.txt')
        if lbl_path.exists():
            seen += 1
            continue
        # read image
        im = cv2.imread(str(img))
        if im is None:
            continue
        h, w = im.shape[:2]
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            continue
        # pick largest
        faces = sorted(faces, key=lambda b: b[2]*b[3], reverse=True)
        bbox = faces[0]
        write_yolo(lbl_path, 0, bbox, w, h)
        wrote += 1
        if wrote >= max_per_split:
            break
    return wrote, seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', default='dataset/images')
    parser.add_argument('--labels-out', default='dataset/labels')
    parser.add_argument('--max-per-split', type=int, default=100000)
    args = parser.parse_args()

    images_root = Path(args.images)
    labels_out = Path(args.labels_out)

    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    total_written = 0
    total_seen = 0
    for split in ['train', 'val']:
        wrote, seen = process_split(images_root, labels_out, split, face_cascade, args.max_per_split)
        print(f"Split '{split}': wrote {wrote} new pseudo-labels; skipped {seen} existing labels")
        total_written += wrote
        total_seen += seen

    print(f"Total pseudo-labels written: {total_written}")


if __name__ == '__main__':
    main()
