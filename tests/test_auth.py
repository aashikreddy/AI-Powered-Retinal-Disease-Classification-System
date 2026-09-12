import requests
import json
import time
from reportlab.pdfgen import canvas
from PIL import Image
import os

API_URL = "http://localhost:5002/api"

def create_valid_pdf():
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save('dummy_img.jpg')
    
    # Create a PDF with the image
    c = canvas.Canvas("dummy.pdf")
    c.drawImage('dummy_img.jpg', 0, 0, 100, 100)
    c.save()

def register(email, password):
    r = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
    if r.status_code == 400 and "already exists" in r.text:
        # try login
        r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return r.json()['token'], r.json()['user']['id']

def upload_pdf(token):
    create_valid_pdf()
    with open("dummy.pdf", "rb") as f:
        r = requests.post(f"{API_URL}/reports/upload", headers={"Authorization": f"Bearer {token}"}, files={"pdf": f})
    return r

def get_history(token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{API_URL}/reports/history", headers=headers)

def download(token, report_id):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{API_URL}/reports/download/{report_id}", headers=headers)

print("--- Registering users ---")
tokenA, idA = register("usera2@example.com", "pass")
tokenB, idB = register("userb2@example.com", "pass")
print(f"User A: {idA}")
print(f"User B: {idB}")

print("\n--- Testing Unauthenticated History ---")
r_unauth = get_history(None)
print(f"Unauthenticated History: {r_unauth.status_code} (Expected 401)")

print("\n--- Uploading Reports ---")
r_uplA = upload_pdf(tokenA)
print(f"Upload A status: {r_uplA.status_code} (Expected 200)")
if r_uplA.status_code != 200:
    print("Upload A failed:", r_uplA.text)

r_uplB = upload_pdf(tokenB)
print(f"Upload B status: {r_uplB.status_code} (Expected 200)")
if r_uplB.status_code != 200:
    print("Upload B failed:", r_uplB.text)

if r_uplA.status_code != 200 or r_uplB.status_code != 200:
    print("Uploads failed, cannot continue.")
    exit(1)

report_id_A = r_uplA.json()['report']['id']
report_id_B = r_uplB.json()['report']['id']
print(f"Report A ID: {report_id_A}")
print(f"Report B ID: {report_id_B}")

print("\n--- Testing History Isolation ---")
historyA = get_history(tokenA).json().get('reports', [])
historyB = get_history(tokenB).json().get('reports', [])
idsA = [r['_id'] for r in historyA]
idsB = [r['_id'] for r in historyB]
print(f"User A History count: {len(historyA)} (Contains A? {report_id_A in idsA}, Contains B? {report_id_B in idsA})")
print(f"User B History count: {len(historyB)} (Contains B? {report_id_B in idsB}, Contains A? {report_id_A in idsB})")

print("\n--- Testing Download Ownership ---")
dl_A_own = download(tokenA, report_id_A)
dl_B_own = download(tokenB, report_id_B)
print(f"A downloads A: {dl_A_own.status_code} (Expected 200)")
print(f"B downloads B: {dl_B_own.status_code} (Expected 200)")

dl_A_other = download(tokenA, report_id_B)
dl_B_other = download(tokenB, report_id_A)
print(f"A downloads B: {dl_A_other.status_code} (Expected 404)")
print(f"B downloads A: {dl_B_other.status_code} (Expected 404)")

print("\n--- Testing Malformed ID ---")
dl_malformed = download(tokenA, "123")
print(f"Malformed ID download: {dl_malformed.status_code} (Expected 400)")

print("\n--- Finished ---")
