import kagglehub
import os
import shutil

print("Downloading test_images/test_images...")
try:
    test_images_path = kagglehub.dataset_download('mariaherrerot/aptos2019', path='test_images/test_images')
    print(f"Downloaded to: {test_images_path}")
    if os.path.exists('test_images'):
        shutil.rmtree('test_images')
    shutil.copytree(test_images_path, 'test_images')
    print("Copied test_images to current directory.")
except Exception as e:
    print(f"Error downloading test_images/test_images: {e}")
