import kagglehub
import os
import shutil
import sys

print("Kagglehub version:", kagglehub.__version__)

try:
    print("Downloading test.csv...")
    csv_path = kagglehub.dataset_download('mariaherrerot/aptos2019', path='test.csv')
    print(f"CSV downloaded to: {csv_path}")
    shutil.copy(csv_path, 'data/test/test.csv')
except Exception as e:
    print(f"Error downloading test.csv: {e}")
    sys.exit(1)

try:
    print("Downloading test_images...")
    images_path = kagglehub.dataset_download('mariaherrerot/aptos2019', path='test_images')
    print(f"Images downloaded to: {images_path}")
    
    dest_dir = 'data/test/test_images'
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    
    if os.path.isdir(images_path):
        shutil.copytree(images_path, dest_dir)
    else:
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(images_path, dest_dir)
    print("Copied test_images.")
except Exception as e:
    print(f"Error downloading test_images: {e}")
    sys.exit(1)

