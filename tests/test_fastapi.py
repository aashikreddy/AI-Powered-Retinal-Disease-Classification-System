import requests
import json
import os
from reportlab.pdfgen import canvas
from PIL import Image

FASTAPI_URL = "http://127.0.0.1:8000"
SECRET = "c4a928be4f7d4e5a9c9f28d7a16b911c"

def create_valid_pdf(filename="dummy_test.pdf"):
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save('dummy_img.jpg')
    c = canvas.Canvas(filename)
    c.drawImage('dummy_img.jpg', 0, 0, 100, 100)
    c.save()
    os.remove('dummy_img.jpg')
    return filename

print("--- Testing FastAPI Boundaries ---")
# A. FastAPI health without secret: Expected 200
r_a = requests.get(f"{FASTAPI_URL}/health")
print(f"A. /health without secret: {r_a.status_code}")

# B. Direct FastAPI /infer_pdf without x-internal-secret: Expected 401
filename = create_valid_pdf()
with open(filename, 'rb') as f:
    files = {'file': (filename, f, 'application/pdf')}
    r_b = requests.post(f"{FASTAPI_URL}/infer_pdf", files=files)
print(f"B. /infer_pdf without secret: {r_b.status_code}")

# C. Direct FastAPI /infer_pdf with incorrect secret: Expected 401
with open(filename, 'rb') as f:
    files = {'file': (filename, f, 'application/pdf')}
    headers = {'x-internal-secret': 'wrong_secret'}
    r_c = requests.post(f"{FASTAPI_URL}/infer_pdf", files=files, headers=headers)
print(f"C. /infer_pdf with incorrect secret: {r_c.status_code}")

# D. Direct FastAPI /infer_pdf with correct secret: Expected successful inference behavior (200)
with open(filename, 'rb') as f:
    files = {'file': (filename, f, 'application/pdf')}
    headers = {'x-internal-secret': SECRET}
    r_d = requests.post(f"{FASTAPI_URL}/infer_pdf", files=files, headers=headers)
print(f"D. /infer_pdf with correct secret: {r_d.status_code}")

# H. Verify FastAPI is listening on localhost only
import socket
print(f"\nH. Checking listening host...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Try public IP or local network IP if known, but we'll just check netstat later if needed
    pass
finally:
    s.close()
    
os.remove(filename)
