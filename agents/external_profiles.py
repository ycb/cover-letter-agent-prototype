import requests
from bs4 import BeautifulSoup
import re

def fetch_public_profile(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)
        return text[:5000]
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_linkedin_summary(text):
    sections = re.split(r'(Experience|About|Education|Skills|Licenses)', text, flags=re.IGNORECASE)
    summary = "\n".join(sections[:4]) if sections else text
    return summary 