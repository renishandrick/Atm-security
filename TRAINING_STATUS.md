# ATM Security Detection System  
GPU-Optimized YOLOv8 Real-Time Object Detection (Face, Mask, Helmet)

## Quick Start (GPU Training Just Started! ✓)

### 1. **Training Status**
- Model: YOLOv8 Medium
- GPU: NVIDIA RTX 3050 Laptop
- Training: 100 epochs, batch size 32
- Dataset: 16,742 train + 4,178 val images (20,920 total)
- Run command:
```bash
python train_gpu_final.py --weights yolov8m.pt --data data.yaml --epochs 100 --batch 32 --device 0
```

### 2. **After Training Completes**
Best model will be saved to: `models/yolov8_atm_security_best.pt`

### 3. **Run Inference**

**On a single image:**
```bash
python inference.py --image path/to/image.jpg --output result.jpg
```

**On webcam:**
```bash
python inference.py --webcam
```

### 4. **Use Trained Model in Your App**
```python
from ultralytics import YOLO

model = YOLO('models/yolov8_atm_security_best.pt')
results = model('path/to/image.jpg', conf=0.5)
for r in results:
    print(r.boxes)  # Detection boxes
```

## Environment

- Python: 3.14
- PyTorch: 2.9.0+cu129 (CUDA 12.9)
- GPU: NVIDIA RTX 3050 Laptop (4.3 GB)
- Ultralytics: YOLOv8

## Dataset Structure
```
dataset/
├── images/
│   ├── train/  (16,742 images)
│   └── val/    (4,178 images)
└── labels/     (YOLO format txt files)
```

## Project Files
- `train_gpu_final.py` - Main GPU training script
- `inference.py` - Inference on images/webcam
- `data.yaml` - YOLO dataset config
- `scripts/run_training.py` - Alternative training wrapper

## Monitoring Training
Training logs saved in: `runs/detect/gpu_train_final/train_gpu/`

View results:
```bash
# After training
ls runs/detect/gpu_train_final/train_gpu/
```

## Tips
- Batch size can be increased to 64 for better GPU utilization (if memory allows)
- Use `--resume` flag to resume interrupted training
- Use `--epochs 50` for quick tests before full 100-epoch run
- Model names: `yolov8n` (nano), `yolov8s` (small), `yolov8m` (medium, currently training), `yolov8l` (large)

## Next Steps
1. ✅ GPU & PyTorch CUDA configured
2. ✅ Ultralytics installed
3. ⏳ **Training in progress** (GPU utilization ~90% on RTX 3050)
4. ⏳ Validation & model saving
5. → Inference on images/webcam

---
*Last updated: Nov 26, 2025 - GPU training started successfully*
