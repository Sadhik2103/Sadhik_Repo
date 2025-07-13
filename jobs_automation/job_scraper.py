import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests

# List of job titles/keywords to search for
JOB_KEYWORDS = [
    "python developer", "software engineer", "software developer", "sql developer",
    "java developer", "backend developer", "flask developer", "AI developer",
    "frontend developer"
]

# List of job platforms to search dynamically (you can add more)
JOB_PLATFORMS = [
    "linkedin.com", "indeed.com", "internshala.com", "naukri.com",
    "monster.com", "glassdoor.com", "foundit.in", "angel.co", "hirect.in", "timesjobs.com"
]

# Email settings
EMAIL = os.environ.get("EMAIL_ADDRESS")
PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
TO_EMAIL = os.environ.get("EMAIL_ADDRESS")  # can add more emails separated by comma

def search_jobs_bing(query, num_results=10):
    """Use Bing Web Search to find relevant job postings."""
    subscription_key = os.environ.get("BING_API_KEY")
    if not subscription_key:
        print("No Bing API Key found in environment. Skipping Bing search.")
        return []
    search_url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query, "count": num_results, "responseFilter": "Webpages"}
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("webPages", {}).get("value", [])
        jobs = []
        for web_result in results:
            jobs.append({
                "title": web_result.get("name"),
                "link": web_result.get("url"),
                "snippet": web_result.get("snippet")
            })
        return jobs
    except Exception as e:
        print(f"Bing search failed: {e}")
        return []

def get_dynamic_job_results():
    """Search for jobs using Bing API for each keyword and platform."""
    all_jobs = []
    for keyword in JOB_KEYWORDS:
        for platform in JOB_PLATFORMS:
            query = f"{keyword} jobs site:{platform}"
            jobs = search_jobs_bing(query)
            for job in jobs:
                # Extract company if possible from title or snippet
                company = ""
                for part in job["title"].split("-"):
                    if "company" in part.lower() or "at" in part.lower():
                        company = part.strip()
                all_jobs.append({
                    "title": job["title"],
                    "company": company,
                    "apply_link": job["link"],
                    "jd_link": job["link"]
                })
    return all_jobs

def deduplicate_jobs(jobs):
    """Remove duplicate job postings based on link."""
    seen = set()
    unique = []
    for job in jobs:
        key = job["apply_link"]
        if key not in seen:
            unique.append(job)
            seen.add(key)
    return unique

def format_jobs_email(jobs):
    if not jobs:
        return "No new jobs found today!"
    lines = []
    for idx, job in enumerate(jobs, 1):
        lines.append(
            f"{idx}. {job['title']}\n"
            f"   Company: {job.get('company', 'N/A')}\n"
            f"   Apply Link: {job['apply_link']}\n"
            f"   JD Link: {job['jd_link']}\n"
        )
    return "\n".join(lines)

def send_email(subject, body, to_email):
    if not (EMAIL and PASSWORD):
        raise Exception("Email credentials not set in environment variables.")
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.sendmail(EMAIL, to_email.split(","), msg.as_string())

if __name__ == "__main__":
    jobs = get_dynamic_job_results()
    jobs = deduplicate_jobs(jobs)
    body = format_jobs_email(jobs)
    subject = f"Daily Dynamic Job Search Results - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, body, TO_EMAIL)
