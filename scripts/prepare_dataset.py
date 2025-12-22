"""Prepare dataset for YOLO training.
This script will:
- Look for class folders under `dataset/` (e.g. `dataset/face`, `dataset/mask`, `dataset/helmet`).
- Split images into `dataset/images/train` and `dataset/images/val` (default 80/20).
- Copy matching label files if present (expects same base filename with `.txt`).
- Report counts and missing labels.

Usage:
    python scripts/prepare_dataset.py --src dataset --out dataset --val-size 0.2
"""
import os
import shutil
import argparse
import random


def is_image_file(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.bmp']


def prepare(src_dir, out_dir, val_size=0.2, seed=42):
    random.seed(seed)
    classes = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    images_out_train = os.path.join(out_dir, 'images', 'train')
    images_out_val = os.path.join(out_dir, 'images', 'val')
    labels_out_train = os.path.join(out_dir, 'labels', 'train')
    labels_out_val = os.path.join(out_dir, 'labels', 'val')

    for p in [images_out_train, images_out_val, labels_out_train, labels_out_val]:
        os.makedirs(p, exist_ok=True)

    total = 0
    missing_labels = {c:0 for c in classes}
    copied = {c:0 for c in classes}

    for cls in classes:
        cls_dir = os.path.join(src_dir, cls)
        # collect images in subfolders as well
        imgs = []
        for root, _, files in os.walk(cls_dir):
            for f in files:
                if is_image_file(f):
                    imgs.append(os.path.join(root, f))

        random.shuffle(imgs)
        n_val = int(len(imgs) * val_size)
        val_imgs = imgs[:n_val]
        train_imgs = imgs[n_val:]

        for img_path in train_imgs:
            total += 1
            fname = os.path.basename(img_path)
            base, _ = os.path.splitext(fname)
            out_img = os.path.join(images_out_train, fname)
            shutil.copy2(img_path, out_img)

            # copy label if exists
            lbl = os.path.join(os.path.dirname(img_path), base + '.txt')
            if os.path.exists(lbl):
                shutil.copy2(lbl, os.path.join(labels_out_train, base + '.txt'))
            else:
                missing_labels[cls] += 1
            copied[cls] += 1

        for img_path in val_imgs:
            total += 1
            fname = os.path.basename(img_path)
            base, _ = os.path.splitext(fname)
            out_img = os.path.join(images_out_val, fname)
            shutil.copy2(img_path, out_img)

            lbl = os.path.join(os.path.dirname(img_path), base + '.txt')
            if os.path.exists(lbl):
                shutil.copy2(lbl, os.path.join(labels_out_val, base + '.txt'))
            else:
                missing_labels[cls] += 1
            copied[cls] += 1

    print(f"Prepared dataset. Total images processed: {total}")
    for c in classes:
        print(f"- Class '{c}': {copied[c]} images; missing labels: {missing_labels[c]}")

    print('\nNotes:')
    print('- Images were copied into dataset/images/{train,val}')
    print('- Labels (if present) were copied into dataset/labels/{train,val}')
    print('- If labels are missing you need to annotate images (LabelImg/CVAT/Roboflow) in YOLO format before training')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='dataset', help='Source dataset folder containing class subfolders')
    parser.add_argument('--out', default='dataset', help='Output base (will create images/ and labels/ under this)')
    parser.add_argument('--val-size', type=float, default=0.2, help='Fraction for validation set')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    prepare(args.src, args.out, args.val_size, args.seed)
