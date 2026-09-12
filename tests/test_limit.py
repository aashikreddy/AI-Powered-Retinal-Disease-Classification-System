import os
import requests
from reportlab.pdfgen import canvas
from PIL import Image

FASTAPI_URL = "http://127.0.0.1:8000"
SECRET = "c4a928be4f7d4e5a9c9f28d7a16b911c"
headers = {'x-internal-secret': SECRET}

def create_image(filename, width, height, color):
    img = Image.new('RGB', (width, height), color=color)
    img.save(filename)

def create_pdf(pdf_name, pages):
    c = canvas.Canvas(pdf_name)
    for page_imgs in pages:
        for img_data in page_imgs:
            c.drawImage(img_data['img'], img_data.get('x', 0), img_data.get('y', 0), width=img_data['w'], height=img_data['h'])
        c.showPage()
    c.save()

# Generate temporary images
create_image('dummy.jpg', 10, 10, 'blue')

print("--- Testing Image Limit ---")

# 1. Exactly 1 image
create_pdf('test1.pdf', [[{'img': 'dummy.jpg', 'w': 10, 'h': 10}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test1.pdf', 'rb')}, headers=headers)
print(f"Test A (1 image): {r.status_code}")

# 2. 10 images
pages = [ [{'img': 'dummy.jpg', 'w': 10, 'h': 10, 'x': i*12}] for i in range(10) ]
create_pdf('test2.pdf', pages)
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test2.pdf', 'rb')}, headers=headers)
print(f"Test B (10 images): {r.status_code}")

# 3. 50 images exactly
pages = [ [{'img': 'dummy.jpg', 'w': 10, 'h': 10}] for _ in range(50) ]
create_pdf('test3.pdf', pages)
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test3.pdf', 'rb')}, headers=headers)
print(f"Test C (50 images): {r.status_code}")

# 4. 51 images (400)
pages = [ [{'img': 'dummy.jpg', 'w': 10, 'h': 10}] for _ in range(51) ]
create_pdf('test4.pdf', pages)
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test4.pdf', 'rb')}, headers=headers)
print(f"Test D (51 images): {r.status_code} - {r.text}")

# Clean up
for f in ['dummy.jpg', 'test1.pdf', 'test2.pdf', 'test3.pdf', 'test4.pdf']:
    try:
        os.remove(f)
    except:
        pass
