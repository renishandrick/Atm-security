# 3 WAYS TO CHECK IF TRAINING IS COMPLETE

## Method 1: Quick Check (Fastest)
Open PowerShell and run:
```powershell
$results = Get-ChildItem -Path "runs/detect/atm_final" -Filter "results.csv" -Recurse -ErrorAction SilentlyContinue
if ($results) {
    $csv = @(Import-Csv $results.FullName)
    $last = $csv[-1]
    Write-Host "Epoch: $($last.Epoch)/100"
    Write-Host "Status: $(if([float]$last.Epoch -ge 99) {'✅ COMPLETE'} else {'🚀 RUNNING'})"
} else {
    Write-Host "Training not started yet"
}
```

## Method 2: Check Best Model File (Simplest)
Open PowerShell and run:
```powershell
if (Test-Path "runs/detect/atm_final/exp1/weights/best.pt") {
    Write-Host "✅ TRAINING COMPLETE! Best model saved."
    ls -la "runs/detect/atm_final/exp1/weights/"
} else {
    Write-Host "⏳ Training still running..."
}
```

## Method 3: Live Monitor (Every 30 seconds)
```powershell
python check_training.py --live
```

## Method 4: Check Process Running
```powershell
tasklist | Select-String python
# If python process still running = training active
```

---

## QUICK INDICATORS

| Sign | Meaning |
|------|---------|
| `best.pt` exists in `runs/detect/atm_final/exp1/weights/` | ✅ Training Done |
| Last CSV row shows Epoch = 99 or 100 | ✅ Training Done |
| Python process running | 🚀 Still Training |
| CSV file growing in size | 🚀 Still Training |
| No changes for 30+ mins | ❌ Might be stuck |

---

## WHAT TO DO WHEN COMPLETE

```powershell
# 1. Copy best model
mkdir models -ErrorAction SilentlyContinue
copy "runs/detect/atm_final/exp1/weights/best.pt" "models/yolov8_atm_security_best.pt"

# 2. Test on image
python inference.py --image test.jpg --output result.jpg

# 3. Test on webcam
python inference.py --webcam
```

---

## BACKGROUND INFO

- Training saves a checkpoint every epoch in `runs/detect/atm_final/exp1/weights/last.pt`
- Best model is automatically saved when performance improves
- When training completes, `results.csv` will have 100 rows (Epoch 0-99)
- ETA: 4-6 hours total on RTX 3050

**TL;DR: Just check if `runs/detect/atm_final/exp1/weights/best.pt` exists. When it does, training is done!**
