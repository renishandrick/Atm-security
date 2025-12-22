"""Dry-check dataset: count images and YOLO .txt labels per class.
Writes a small report and a `dataset/missing_labels.txt` file with missing image paths (one per line).
"""
import os
import argparse


def is_image_file(name):
    return os.path.splitext(name)[1].lower() in ['.jpg', '.jpeg', '.png', '.bmp']


def main(src_dir='dataset', out_missing='dataset/missing_labels.txt', max_examples=10):
    classes = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    report = []
    missing_overall = []

    for cls in classes:
        cls_dir = os.path.join(src_dir, cls)
        imgs = []
        labels = set()
        for root, _, files in os.walk(cls_dir):
            for f in files:
                if is_image_file(f):
                    imgs.append(os.path.join(root, f))
                elif f.lower().endswith('.txt'):
                    labels.add(os.path.splitext(f)[0])

        missing = []
        for img in imgs:
            base = os.path.splitext(os.path.basename(img))[0]
            if base not in labels:
                missing.append(img)

        report.append((cls, len(imgs), len(labels), len(missing)))
        missing_overall.extend(missing)

        print(f"Class '{cls}': images={len(imgs)}, labels={len(labels)}, missing_labels={len(missing)}")
        if missing:
            print(f"  Examples missing (up to {max_examples}):")
            for p in missing[:max_examples]:
                print('   -', p)

    print('\nTotal classes:', len(classes))
    print('Total images missing labels:', len(missing_overall))

    # write missing list
    with open(out_missing, 'w', encoding='utf-8') as f:
        for p in missing_overall:
            f.write(p.replace('\\', '/') + '\n')

    print(f"Wrote missing image list to: {out_missing}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='dataset')
    parser.add_argument('--out', default='dataset/missing_labels.txt')
    parser.add_argument('--examples', type=int, default=10)
    args = parser.parse_args()
    main(args.src, args.out, args.examples)
