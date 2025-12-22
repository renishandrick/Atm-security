# Annotation Guide — Manual Labeling Workflow

This guide describes how to annotate images in YOLO format using LabelImg (Windows) and how to prepare labels for training with the project's `data.yaml`.

Steps (quick):

1. Install LabelImg (recommended):

   - Using pip (inside your `atm_env` virtualenv):

     ```powershell
     C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe -m pip install labelImg
     labelImg
     ```

   - Or download the prebuilt Windows binary from the LabelImg release page.

2. Launch LabelImg and set the default Save Dir to a folder inside the project (for example `dataset/label_sample` when working on a small set or `dataset/labels_raw` for full runs).

3. When annotating, choose the `YOLO` annotation format in LabelImg (top-right selector). Save annotations — each image will get a `.txt` file with the same basename.

4. Suggested workflow:
   - Create a small sample to annotate first:

     ```powershell
     C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe scripts\create_label_sample.py --src dataset --out dataset/label_sample --count 200
     ```

   - Annotate the sample in LabelImg, verify YOLO `.txt` files are written next to images.

5. After labeling is done, run the label sync tool to copy/convert labels next to the images in `dataset/images/{train,val}` and place YOLO `.txt` files into `dataset/labels/{train,val}`:

   ```powershell
   C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe scripts\sync_labels.py --images dataset/images --labels-src dataset/label_sample --out dataset/labels --val-size 0.2
   ```

6. Run the dry-check to confirm everything is aligned:

   ```powershell
   C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe scripts\dry_check_labels.py --src dataset --out dataset/missing_labels.txt
   ```

7. Train the model (small test run first):

   ```powershell
   C:\Users\renish\OneDrive\Desktop\atmsec\atm_env\Scripts\python.exe scripts\run_training.py --weights yolov8n.pt --epochs 10 --batch 16
   ```

Notes
- If your annotations are in Pascal VOC (`.xml`) format, the `sync_labels.py` tool will attempt to convert them to YOLO using the default class names `['face','mask','helmet']`. If your class names differ, pass `--names "face,mask,helmet"`.
- If you have COCO `.json` annotations, tell me and I will add a converter.

If you want, I can create a short tutorial GIF showing LabelImg setup and annotation.
