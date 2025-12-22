import argparse
import random
import shutil
from pathlib import Path


def is_image(fn: Path):
    return fn.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}


def gather_images(src: Path):
    return [p for p in src.rglob('*') if p.is_file() and is_image(p)]


def copy_sample(src: Path, out: Path, count: int, seed: int = 42):
    imgs = gather_images(src)
    if not imgs:
        print('No images found under', src)
        return 0
    random.seed(seed)
    sample = random.sample(imgs, min(count, len(imgs)))
    for img in sample:
        rel = img.relative_to(src)
        dest_img = out / 'images' / rel
        dest_img.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img, dest_img)
        # copy existing label if present
        txt = img.with_suffix('.txt')
        if txt.exists():
            dest_txt = out / 'images' / rel.with_suffix('.txt')
            shutil.copy2(txt, dest_txt)
    print(f'Copied {len(sample)} images to {out / "images"}')
    return len(sample)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='dataset', help='Source dataset root to sample from')
    parser.add_argument('--out', default='dataset/label_sample', help='Output sample folder')
    parser.add_argument('--count', type=int, default=200, help='How many images to sample')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    copied = copy_sample(src, out, args.count, args.seed)
    print('Done')


if __name__ == '__main__':
    main()
