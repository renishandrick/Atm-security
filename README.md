# ATM Security System — Project Setup

Quick steps to get this project running locally.

Prerequisites
- Python 3.10+ (you already have a virtualenv in `atm_env`)
- `atm_env` virtual environment activated or use full path to the env python

Install dependencies (if not done):
```powershell
C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe -m pip install -r requirements.txt
```

Prepare dataset (split images into train/val and copy labels if present):
```powershell
python scripts/prepare_dataset.py --src dataset --out dataset --val-size 0.2
```

Training (requires YOLO `data.yaml` and labels in YOLO format):
```powershell
python train.py
```

Run inference (live webcam):
```powershell
python atm_security_final.py --model runs/detect/train/weights/best.pt
# if you don't have trained weights, the script will fallback to 'yolov8n.pt' or automatically
# download 'yolov8n' from Ultralytics.
```

Notes
- Your current dataset images are under `dataset/` in class folders. The repository did not contain YOLO label `.txt` files. You must annotate images (LabelImg/CVAT/Roboflow) to train a supervised detector.
- `scripts/prepare_dataset.py` will copy images and labels (if any) into `dataset/images/{train,val}` and `dataset/labels/{train,val}`.
