# organize_for_roboflow.py
import os
import random
import shutil

print("📁 ORGANIZING DATASETS FOR ROBoFLOW")
print("=" * 40)

def get_sample_images(source_folder, dest_folder, max_samples=200):
    """Copy sample images for annotation"""
    if not os.path.exists(source_folder):
        print(f"❌ Source folder not found: {source_folder}")
        return 0
        
    images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    # Take random sample (so you don't have to annotate thousands)
    if len(images) > max_samples:
        images = random.sample(images, max_samples)
        print(f"📦 Taking {max_samples} sample images from {len(images)} total")
    
    # Copy to destination
    os.makedirs(dest_folder, exist_ok=True)
    for img in images:
        src = os.path.join(source_folder, img)
        dst = os.path.join(dest_folder, img)
        shutil.copy2(src, dst)
    
    return len(images)

# Create organized folder for Roboflow
os.makedirs('roboflow_upload', exist_ok=True)

print("\n🎯 Preparing samples for Roboflow annotation...")

# Copy samples from each dataset
face_count = get_sample_images('dataset/face', 'roboflow_upload/face', 150)
mask_count = get_sample_images('dataset/mask', 'roboflow_upload/mask', 150) 
helmet_count = get_sample_images('dataset/helmet', 'roboflow_upload/helmet', 150)

print(f"\n📊 SAMPLES READY FOR ROBoFLOW:")
print(f"   Face: {face_count} images")
print(f"   Mask: {mask_count} images")
print(f"   Helmet: {helmet_count} images")

print(f"\n📁 Total images for annotation: {face_count + mask_count + helmet_count}")
print("\n🎯 NEXT: Upload ALL images from 'roboflow_upload/' folder to Roboflow")
print("   This gives you 450+ images to annotate (good for training)")