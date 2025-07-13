from job_scraper import search_jobs
from mailer import send_email

def main():
    keywords = ["python developer", "software engineer", "software developer", 
                "SQL", "java", "backend", "flask", "AI"]
    results = search_jobs(keywords)
    send_email(["shaiksadhik021@gmail.com"], results)

if __name__ == "__main__":
    main()
