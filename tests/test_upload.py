import requests
import json
import os
import time
from reportlab.pdfgen import canvas
from PIL import Image

API_URL = "http://localhost:5002/api"

def create_valid_pdf(filename="dummy.pdf"):
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save('dummy_img.jpg')
    c = canvas.Canvas(filename)
    c.drawImage('dummy_img.jpg', 0, 0, 100, 100)
    c.save()
    os.remove('dummy_img.jpg')

def create_no_image_pdf(filename="dummy_no_image.pdf"):
    c = canvas.Canvas(filename)
    c.drawString(100, 100, "Hello World")
    c.save()

def register(email, password):
    r = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
    if r.status_code == 400 and "already exists" in r.text:
        r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return r.json()['token'], r.json()['user']['id']

def upload(token, filename, content=None, mimetype='application/pdf', custom_name=None):
    if content is None:
        with open(filename, "rb") as f:
            content = f.read()
    files = {"pdf": (custom_name or filename, content, mimetype)}
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/reports/upload", headers=headers, files=files)

print("--- Registering test user ---")
tokenA, idA = register("usertest@example.com", "pass")

print("\nA. Testing Valid PDF")
create_valid_pdf("valid.pdf")
r_valid = upload(tokenA, "valid.pdf")
print(f"Valid PDF: {r_valid.status_code} (Expected 200)")

print("\nB. Testing Wrong Extension")
with open("valid.jpg", "wb") as f:
    f.write(b"fake image data")
r_ext = upload(tokenA, "valid.jpg", mimetype="application/pdf")
print(f"Wrong Extension: {r_ext.status_code} (Expected 400 if FastAPI rejects, wait, FastAPI checks endswith('.pdf'). FastAPI returns 400. Let's see what happens.)")
print("Response:", r_ext.text)

print("\nC. Testing Wrong MIME Type")
r_mime = upload(tokenA, "valid.pdf", mimetype="image/jpeg")
print(f"Wrong MIME: {r_mime.status_code} (Expected 400)")
print("Response:", r_mime.text)

print("\nD. Testing PDF > 10MB")
large_content = b"%PDF-1.4\n" + (b"A" * 11 * 1024 * 1024)
r_large = upload(tokenA, "large.pdf", content=large_content)
print(f"Large PDF: {r_large.status_code} (Expected 400)")
print("Response:", r_large.text)

print("\nE. Testing 0-byte PDF")
r_zero = upload(tokenA, "zero.pdf", content=b"")
print(f"0-byte PDF: {r_zero.status_code} (Expected 400)")
print("Response:", r_zero.text)

print("\nF. Testing Corrupted PDF")
r_corrupt = upload(tokenA, "corrupt.pdf", content=b"%PDF-1.4\ncorrupted")
print(f"Corrupted PDF: {r_corrupt.status_code} (Expected 400)")
print("Response:", r_corrupt.text)

print("\nG. Testing Valid PDF no images")
create_no_image_pdf("no_img.pdf")
r_noimg = upload(tokenA, "no_img.pdf")
print(f"No Images PDF: {r_noimg.status_code} (Expected 400)")
print("Response:", r_noimg.text)

print("\nH. Testing Filename Traversal")
r_trav = upload(tokenA, "valid.pdf", custom_name="../../../test.pdf")
print(f"Traversal Filename: {r_trav.status_code} (Expected 200 or safe 400)")
print("Response:", r_trav.text)

print("\nI/J. Cleanup Check")
uploads_dir = os.path.join("backend", "uploads")
temp_dir = os.path.join("backend", "temp_inference")
print(f"Uploads dir empty? {len(os.listdir(uploads_dir)) == 0 if os.path.exists(uploads_dir) else True}")
print(f"Temp dir empty? {len(os.listdir(temp_dir)) == 0 if os.path.exists(temp_dir) else True}")

print("\nK. Phase 24 Regression")
tokenB, idB = register("userb_reg@example.com", "pass")
report_id_A = r_valid.json().get('report', {}).get('id', '')
if report_id_A:
    r_dl_other = requests.get(f"{API_URL}/reports/download/{report_id_A}", headers={"Authorization": f"Bearer {tokenB}"})
    print(f"Cross-user download: {r_dl_other.status_code} (Expected 404)")
    r_dl_malformed = requests.get(f"{API_URL}/reports/download/123", headers={"Authorization": f"Bearer {tokenA}"})
    print(f"Malformed ID: {r_dl_malformed.status_code} (Expected 400)")

print("\nDone")
