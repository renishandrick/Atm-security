"""Sync and convert labels into YOLO format next to images in dataset images folders.

This script will:
- Walk `--images` directory (expects `train`/`val` or class subfolders)
- For each image, look for a `.txt` (YOLO) or `.xml` (Pascal VOC) with the same basename in the provided `--labels-src` directories.
- Convert `.xml` to YOLO if needed using the provided class names.
- Write YOLO `.txt` files into `--out` keeping `train`/`val` structure.
"""

import argparse
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image
from typing import List


def is_image(p: Path):
    return p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}


def voc_to_yolo(xml_path: Path, img_w: int, img_h: int, names: List[str]):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    out_lines = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name not in names:
            continue
        cls = names.index(name)
        b = obj.find('bndbox')
        xmin = float(b.find('xmin').text)
        ymin = float(b.find('ymin').text)
        xmax = float(b.find('xmax').text)
        ymax = float(b.find('ymax').text)
        x_center = (xmin + xmax) / 2.0 / img_w
        y_center = (ymin + ymax) / 2.0 / img_h
        w = (xmax - xmin) / img_w
        h = (ymax - ymin) / img_h
        out_lines.append(f"{cls} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
    return out_lines


def find_label_for_image(img: Path, label_dirs: List[Path]):
    stem = img.stem
    for d in label_dirs:
        txt = d / (img.parent.name) / (stem + '.txt')
        if txt.exists():
            return txt
        txt2 = img.with_suffix('.txt')
        if txt2.exists():
            return txt2
        xml = d / (img.parent.name) / (stem + '.xml')
        if xml.exists():
            return xml
        # Check flat root
        flat_txt = d / (stem + '.txt')
        if flat_txt.exists():
            return flat_txt
        flat_xml = d / (stem + '.xml')
        if flat_xml.exists():
            return flat_xml
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', default='dataset/images', help='Root of images (train/val)')
    parser.add_argument('--labels-src', default='dataset', help='Comma-separated label source dirs')
    parser.add_argument('--out', default='dataset/labels', help='Output labels root (will contain train/val)')
    parser.add_argument('--names', default='face,mask,helmet', help='Comma-separated class names in order')
    parser.add_argument('--val-size', type=float, default=0.2, help='If images are not split, create val split (not used for copying)')
    args = parser.parse_args()
    images_root = Path(args.images)
    label_srcs = [Path(p.strip()) for p in args.labels_src.split(',')]
    out_root = Path(args.out)
    names = [n.strip() for n in args.names.split(',')]

    if not images_root.exists():
        print('Images root not found:', images_root)
        return

    out_root.mkdir(parents=True, exist_ok=True)

    images = [p for p in images_root.rglob('*') if p.is_file() and is_image(p)]
    missing = []
    converted = 0
    copied = 0
    for img in images:
        label = find_label_for_image(img, label_srcs)
        dest_dir = out_root / img.parent.relative_to(images_root)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_txt = dest_dir / (img.stem + '.txt')
        if label is None:
            missing.append(str(img))
            continue
        if label.suffix.lower() == '.txt':
            shutil.copy2(label, dest_txt)
            copied += 1
        elif label.suffix.lower() == '.xml':
            with Image.open(img) as im:
                w, h = im.size
            lines = voc_to_yolo(label, w, h, names)
            if lines:
                dest_txt.write_text('\n'.join(lines))
                converted += 1
            else:
                missing.append(str(img))
        else:
            missing.append(str(img))

    print(f'Processed {len(images)} images')
    print(f'Copied {copied} existing YOLO .txt labels')
    print(f'Converted {converted} Pascal VOC .xml labels')
    print(f'Missing labels for {len(missing)} images')
    missing_file = out_root.parent / 'missing_labels_sync.txt'
    missing_file.write_text('\n'.join(missing))
    print('Wrote missing list to', missing_file)


if __name__ == '__main__':
    main()
