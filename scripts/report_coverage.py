from pathlib import Path


def is_image(p: Path):
    return p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}


def main():
    root = Path('dataset')
    img_root = root / 'images'
    lbl_root = root / 'labels'

    img_count = 0
    for p in img_root.rglob('*'):
        if p.is_file() and is_image(p):
            img_count += 1

    lbl_count = 0
    if lbl_root.exists():
        for p in lbl_root.rglob('*.txt'):
            if p.is_file():
                lbl_count += 1

    report = f"images={img_count}\nlabels={lbl_count}\n"
    out = root / 'coverage_report.txt'
    out.write_text(report)
    print(report)


if __name__ == '__main__':
    main()
