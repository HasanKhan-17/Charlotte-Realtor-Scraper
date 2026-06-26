import os
import sys
import requests
import pandas as pd

API_KEY = os.getenv("SERPER_API_KEY")

if not API_KEY:
    raise Exception("SERPER_API_KEY not found.")

industry = sys.argv[1]
city = sys.argv[2]
state = sys.argv[3]
lead_limit = int(sys.argv[4])

query = f"{industry} in {city}, {state}"

url = "https://google.serper.dev/search"

payload = {
    "q": query,
    "num": 100
}

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

data = response.json()

print(data)