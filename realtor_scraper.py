import os
import sys
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

print("===== SCRIPT STARTED =====")

API_KEY = os.getenv("SERPER_API_KEY")

if not API_KEY:
    raise Exception("SERPER_API_KEY not found.")

print("API KEY FOUND")

industry = sys.argv[1]
city = sys.argv[2]
state = sys.argv[3]
lead_limit = int(sys.argv[4])

query = f"{industry} in {city}, {state}"

print(f"Searching: {query}")

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(
    "https://google.serper.dev/search",
    headers=headers,
    json={
        "q": query,
        "num": 100
    }
)

print("Search Status:", response.status_code)

data = response.json()

results = data.get("organic", [])

print(f"Found {len(results)} search results")

rows = []

email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
phone_pattern = re.compile(r'(\+?\d[\d\-\(\) ]{8,}\d)')

for result in results:

    website = result.get("link")

    if not website:
        continue

    print(f"Checking {website}")

    try:

        response = requests.get(
            website,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        emails = list(set(email_pattern.findall(text)))
        phones = list(set(phone_pattern.findall(text)))

        rows.append({
            "Business": result.get("title", ""),
            "Website": website,
            "Email": ", ".join(emails),
            "Phone": ", ".join(phones)
        })

        print(
            f"Emails: {len(emails)} | Phones: {len(phones)}"
        )

    except Exception as e:
        print(f"ERROR: {website}")
        print(str(e))

    if len(rows) >= lead_limit:
        break

os.makedirs("output", exist_ok=True)

df = pd.DataFrame(rows)

print(df.head())

output_file = "output/leads.xlsx"

df.to_excel(output_file, index=False)

print(f"Saved {len(df)} leads to {output_file}")

print("===== DONE =====")