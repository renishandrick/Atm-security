# verify_final.py
import os
import cv2

print("🔍 FINAL DATASET VERIFICATION")
print("=" * 40)

datasets = ['face', 'mask', 'helmet']
total_images = 0

for dataset in datasets:
    folder_path = f'dataset/{dataset}'
    if os.path.exists(folder_path):
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        print(f"✅ {dataset.upper()}: {len(images)} images")
        total_images += len(images)
        
        # Show first 3 files
        if images:
            print(f"   Sample files: {images[:3]}")
    else:
        print(f"❌ {dataset.upper()}: Folder not found")

print(f"\n📊 TOTAL IMAGES: {total_images}")

if total_images >= 100:
    print("🎉 SUCCESS! You have enough data for training!")
    print("🚀 Proceed to Roboflow annotation")
else:
    print("⚠️  You need more images (aim for 100+ per class)")

print("\n🎯 NEXT: Run 'python organize_for_roboflow.py'")