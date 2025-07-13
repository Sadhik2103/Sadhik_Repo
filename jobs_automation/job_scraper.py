import requests
from bs4 import BeautifulSoup

def search_jobs(keywords):
    listings = []
    for kw in keywords:
        resp = requests.get(f"https://www.indeed.com/jobs?q={kw}")
        soup = BeautifulSoup(resp.text, "html.parser")
        for job in soup.select(".job_seen_beacon h2 a")[:5]:
            title = job.get_text(strip=True)
            link = "https://indeed.com" + job["href"]
            listings.append(f"{title} — {link}")
    return "\n".join(listings)
