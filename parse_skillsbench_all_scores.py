import urllib.request
import re

url = "https://arxiv.org/html/2602.12670v1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all('table')
        for t in tables:
            text = t.get_text(" ", strip=True)
            if "Gemini 3 Flash" in text and "Opus" in text:
                print("Found target table:")
                print(text)
except Exception as e:
    print(f"Error: {e}")
