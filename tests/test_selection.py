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
create_image('small_logo.jpg', 50, 50, 'blue')
create_image('large_retina.jpg', 500, 500, 'red')
create_image('med_retina.jpg', 300, 300, 'green')

print("--- Testing Image Selection ---")

# 1. Single-image PDF
create_pdf('test1.pdf', [[{'img': 'large_retina.jpg', 'w': 500, 'h': 500}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test1.pdf', 'rb')}, headers=headers)
print(f"Test 1 (Single): {r.status_code}")

# 2. PDF containing a small logo + large retinal image
create_pdf('test2.pdf', [[{'img': 'small_logo.jpg', 'w': 50, 'h': 50}, {'img': 'large_retina.jpg', 'w': 500, 'h': 500, 'x': 60}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test2.pdf', 'rb')}, headers=headers)
print(f"Test 2 (Small + Large): {r.status_code}")

# 3. PDF containing large image + small logo
create_pdf('test3.pdf', [[{'img': 'large_retina.jpg', 'w': 500, 'h': 500}, {'img': 'small_logo.jpg', 'w': 50, 'h': 50, 'x': 510}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test3.pdf', 'rb')}, headers=headers)
print(f"Test 3 (Large + Small): {r.status_code}")

# 4. PDF containing multiple retinal images
create_pdf('test4.pdf', [[{'img': 'med_retina.jpg', 'w': 300, 'h': 300}, {'img': 'large_retina.jpg', 'w': 500, 'h': 500, 'x': 310}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test4.pdf', 'rb')}, headers=headers)
print(f"Test 4 (Med + Large): {r.status_code}")

# 5. Multiple pages
create_pdf('test5.pdf', [[{'img': 'small_logo.jpg', 'w': 50, 'h': 50}], [{'img': 'large_retina.jpg', 'w': 500, 'h': 500}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test5.pdf', 'rb')}, headers=headers)
print(f"Test 5 (Multi-page): {r.status_code}")

# 6. Equal-sized images
create_pdf('test6.pdf', [[{'img': 'med_retina.jpg', 'w': 300, 'h': 300}, {'img': 'med_retina.jpg', 'w': 300, 'h': 300, 'x': 310}]])
r = requests.post(f"{FASTAPI_URL}/infer_pdf", files={'file': open('test6.pdf', 'rb')}, headers=headers)
print(f"Test 6 (Equal-size): {r.status_code}")

# Clean up
for f in ['small_logo.jpg', 'large_retina.jpg', 'med_retina.jpg', 'test1.pdf', 'test2.pdf', 'test3.pdf', 'test4.pdf', 'test5.pdf', 'test6.pdf']:
    try:
        os.remove(f)
    except:
        pass
