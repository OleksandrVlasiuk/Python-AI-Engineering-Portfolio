# ==============================================================================
# API PERFORMANCE & LOAD TESTING SCRIPT
# This script simulates a barrage of client requests to measure the Average
# Latency (ms) and System Throughput (requests/sec) of the deployment.
# ==============================================================================

import requests
import time
import sys

# .\venv\Scripts\activate
# python test_perf.py

URL = "http://127.0.0.1:8000/predict"
IMAGE_PATH = "test.jpg"
NUM_REQUESTS = 100

try:
    with open(IMAGE_PATH, 'rb') as f:
        img_data = f.read()
except:
    print(f"Error: test image file '{IMAGE_PATH}' not found!")
    sys.exit()

print(f"Initiating payload test with {NUM_REQUESTS} concurrent requests...")
latencies = []
start_total = time.time()

for i in range(NUM_REQUESTS):
    start_req = time.time()
    resp = requests.post(URL, files={'file': ('test.jpg', img_data, 'image/jpeg')})
    if resp.status_code == 200:
        latencies.append((time.time() - start_req) * 1000)
    else:
        print(f"⚠️ Request {i} failed with status code: {resp.status_code}")

total_time = time.time() - start_total

if len(latencies) == 0:
    print("\n❌ No requests succeeded. Please check the server logs!")
else:
    print(f"\n--- PERFORMANCE RESULTS ({len(latencies)} successful requests) ---")
    print(f"Average Latency: {sum(latencies)/len(latencies):.2f} ms")
    print(f"System Throughput: {len(latencies)/total_time:.2f} req/sec")