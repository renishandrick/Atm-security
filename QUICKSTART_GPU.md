# ATM Security Detection - Complete Setup ✓

**Status: GPU Training In Progress! 🚀**

## What Just Happened

✅ **Environment Setup Complete:**
- Python 3.14 configured
- PyTorch 2.9.0+CUDA 12.9 installed
- NVIDIA RTX 3050 Laptop GPU detected (4.3 GB)
- Ultralytics YOLOv8 installed
- Dataset ready: 20,920 images (16,742 train + 4,178 val)

✅ **GPU Training Started:**
```bash
python train_simple.py
# Runs: 100 epochs, batch size 32, YOLOv8 Medium
# Output: runs/detect/atm_security_final/train_100epochs/
```

---

## Monitor Training Progress

Open a new terminal and run:
```bash
python monitor_training.py
```

This will show real-time metrics:
- Box loss, Class loss, Object loss
- Mean Average Precision (mAP50)
- Updated every 30 seconds

---

## After Training Completes

### 1. **Run Inference on Image**
```bash
python inference.py --image path/to/image.jpg --output result.jpg
```

### 2. **Use Webcam**
```bash
python inference.py --webcam
```

### 3. **Use Model in Code**
```python
from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO('models/yolov8_atm_security_best.pt')

# On image
image = cv2.imread('test.jpg')
results = model(image, conf=0.5)

# On webcam
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    results = model(frame, conf=0.5)
    # Process results...
```

---

## Project Structure

```
atmsec/
├── train_simple.py              # GPU training script (RUNNING)
├── monitor_training.py          # Real-time progress monitor
├── inference.py                 # Inference on images/webcam
├── train_gpu_final.py           # Full-featured training script
├── data.yaml                    # YOLO dataset config
├── yolov8m.pt                   # Model weights (pre-trained)
│
├── dataset/
│   ├── images/
│   │   ├── train/  (16,742 images)
│   │   └── val/    (4,178 images)
│   └── labels/     (YOLO .txt files)
│
├── runs/
│   └── detect/
│       └── atm_security_final/  # Training output (in progress)
│           └── train_100epochs/
│               ├── weights/
│               │   ├── best.pt      ← Best model (saved here after training)
│               │   └── last.pt      ← Last checkpoint
│               ├── results.csv      ← Training metrics
│               └── events.out*      ← TensorBoard logs
│
└── models/
    └── yolov8_atm_security_best.pt  ← Final model (created after training)
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| **Start training** | `python train_simple.py` |
| **Monitor progress** | `python monitor_training.py` |
| **Inference (image)** | `python inference.py --image photo.jpg --output result.jpg` |
| **Inference (webcam)** | `python inference.py --webcam` |
| **Check GPU** | `python -c "import torch; print(torch.cuda.is_available())"` |
| **List trained models** | `ls models/` |

---

## Training Info

| Parameter | Value |
|-----------|-------|
| Model | YOLOv8 Medium |
| GPU | NVIDIA RTX 3050 Laptop |
| Epochs | 100 |
| Batch Size | 32 |
| Image Size | 640×640 |
| Learning Rate | Auto |
| Classes | 3 (face, mask, helmet) |
| Training Data | 16,742 images |
| Validation Data | 4,178 images |

**ETA:** ~4-6 hours on RTX 3050

---

## Troubleshooting

### ❌ Training stopped/crashed
1. Check monitor: `python monitor_training.py`
2. View full logs: `cat runs/detect/atm_security_final/train_100epochs/events.out*`
3. Resume training: Edit `train_simple.py`, add `resume=True` and re-run

### ❌ GPU not detected  
```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

### ❌ Inference says "Model not found"
Make sure training completed and model exists:
```bash
ls -la models/
# Should show: yolov8_atm_security_best.pt
```

---

## Next Steps

1. ⏳ **Wait for training to finish** (monitor with `monitor_training.py`)
2. ✅ **Best model will be saved to:** `models/yolov8_atm_security_best.pt`
3. ✅ **Run inference:** `python inference.py --webcam`
4. ✅ **Deploy in your app:** Import and use the trained model

---

## Model Performance Expectations

- **Inference Speed:** ~50-100ms per frame on RTX 3050
- **Accuracy:** Depends on label quality (typically 60-85% mAP50 for object detection)
- **Classes:** face, mask, helmet

---

**Last Updated:** Nov 26, 2025 - GPU Training In Progress 🔥
