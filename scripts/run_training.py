"""Small wrapper to run YOLOv8 training via Ultralytics API.

Usage (example):
  python scripts/run_training.py --weights yolov8n.pt --data data.yaml --epochs 10 --batch 16
"""

import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', default='yolov8n.pt', help='Initial weights or .pt checkpoint')
    parser.add_argument('--data', default='data.yaml', help='Data config (YOLO format)')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--project', default='runs/detect/train', help='Ultralytics runs project dir')
    parser.add_argument('--device', default=None, help='Device to use for training, e.g. 0 or "cpu" or "cuda:0"')
    args = parser.parse_args()

    print('Starting training with:', args)
    model = YOLO(args.weights)
    # Pass device to training if provided
    train_kwargs = dict(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, project=args.project)
    if args.device:
      train_kwargs['device'] = args.device
    model.train(**train_kwargs)


if __name__ == '__main__':
    main()
