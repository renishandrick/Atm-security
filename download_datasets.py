# download_datasets.py
import os
import zipfile
import requests
import shutil
from pathlib import Path

def create_folders():
    """Create folder structure"""
    folders = ['face', 'mask', 'helmet']
    for folder in folders:
        os.makedirs(f'dataset/{folder}', exist_ok=True)
    print("✅ Folder structure created")

def download_sample_images():
    """Download sample images for testing"""
    print("📥 Downloading sample images...")
    
    # Sample image URLs (you can replace these with actual dataset links)
    sample_urls = {
        'face': [
            'https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg',
        ],
        'mask': [
            'https://www.dropbox.com/s/example1/mask1.jpg?dl=1',  # Replace with actual URLs
        ],
        'helmet': [
            'https://www.dropbox.com/s/example2/helmet1.jpg?dl=1',  # Replace with actual URLs
        ]
    }
    
    print("⚠️  Please download datasets manually from Kaggle for better quality")
    print("🔗 Face dataset: https://www.kaggle.com/datasets/tapakah68/face-detection")
    print("🔗 Mask dataset: https://www.kaggle.com/datasets/andrewmvd/face-mask-detection") 
    print("🔗 Helmet dataset: https://www.kaggle.com/datasets/andrewmvd/hard-hat-detection")

if __name__ == "__main__":
    create_folders()
    download_sample_images()
    print("\n🎯 NEXT STEPS:")
    print("1. Download datasets from Kaggle links above")
    print("2. Extract images to dataset/face/, dataset/mask/, dataset/helmet/")
    print("3. Continue with Roboflow annotation")