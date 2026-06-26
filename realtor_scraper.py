import os
import sys
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

API_KEY = os.getenv("SERPER_API_KEY")

industry = sys.argv[1]
city = sys.argv[2]
state = sys.argv[3]
lead_limit = int(sys.argv[4])

query = f"{industry} in {city}, {state}"

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(
    "https://google.serper.dev/search",
    headers=headers,
    json={"q": query, "num": 100}
)

results = response.json().get("organic", [])

rows = []

email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
phone_pattern = re.compile(r'(\+?\d[\d\-\(\) ]{8,}\d)')

for result in results:

    website = result.get("link")

    print("Checking:", website)

    try:

        html = requests.get(
            website,
            timeout=10,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        ).text

        soup = BeautifulSoup(html,"html.parser")

        text = soup.get_text(" ", strip=True)

        emails = list(set(email_pattern.findall(text)))

        phones = list(set(phone_pattern.findall(text)))

        rows.append({
            "Business": result.get("title"),
            "Website": website,
            "Email": ", ".join(emails),
            "Phone": ", ".join(phones)
        })

    except Exception:
        pass

    if len(rows) >= lead_limit:
        break

os.makedirs("output",exist_ok=True)

df = pd.DataFrame(rows)

df.to_excel("output/leads.xlsx",index=False)

print(df.head())

print("Done.")