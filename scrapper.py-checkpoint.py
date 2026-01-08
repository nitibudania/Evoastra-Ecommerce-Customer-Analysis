from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# JOB ROLES TO SCRAPE

JOB_ROLES = {
    "Support": "https://remoteok.com/remote-support-jobs",
    "Engineer": "https://remoteok.com/remote-engineer-jobs",
    "Software": "https://remoteok.com/remote-software-jobs",
    "Senior": "https://remoteok.com/remote-senior-jobs",
    "Technical": "https://remoteok.com/remote-technical-jobs",
    "Management": "https://remoteok.com/remote-management-jobs",
    "Growth": "https://remoteok.com/remote-growth-jobs",
    "Design": "https://remoteok.com/remote-design-jobs",
    "Lead": "https://remoteok.com/remote-lead-jobs",
    "Financial": "https://remoteok.com/remote-financial-jobs",
    "Sales": "https://remoteok.com/remote-sales-jobs",
    "Marketing": "https://remoteok.com/remote-marketing-jobs",
    "Security": "https://remoteok.com/remote-security-jobs",
    "Cloud": "https://remoteok.com/remote-cloud-jobs",
    "Operations": "https://remoteok.com/remote-operations-jobs",
    "System": "https://remoteok.com/remote-system-jobs",
    "Operational": "https://remoteok.com/remote-operational-jobs",
    "Strategy": "https://remoteok.com/remote-strategy-jobs",
    "Code": "https://remoteok.com/remote-code-jobs",
    "Non Tech": "https://remoteok.com/remote-non-tech-jobs",
    "Healthcare": "https://remoteok.com/remote-healthcare-jobs",
    "Testing": "https://remoteok.com/remote-testing-jobs",
    "SaaS": "https://remoteok.com/remote-saas-jobs",
    "Education": "https://remoteok.com/remote-education-jobs",
    "Video": "https://remoteok.com/remote-video-jobs",
    "Investment": "https://remoteok.com/remote-investment-jobs",
    "Consulting": "https://remoteok.com/remote-consulting-jobs",
    "Medical": "https://remoteok.com/remote-medical-jobs",
    "Voice": "https://remoteok.com/remote-voice-jobs",
    "Architect": "https://remoteok.com/remote-architect-jobs",
    "Golang": "https://remoteok.com/remote-golang-jobs"
}

SCROLL_PAUSE = 2
NUM_SCROLLS = 15


JOB_ATTRIBUTES = {
    "remote", "worldwide", "global", "full-time", "full time",
    "part-time", "part time", "contract", "freelance",
    "internship", "intern", "temporary", "permanent",
    "visa", "relocation", "anywhere", "flexible"
}

# DRIVER SETUP

def get_driver():
    chrome_options = Options()

    # chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# TAG CLASSIFIER

def classify_tags(tags):
    technical_skills = []
    job_attributes = []

    for tag in tags:
        tag_clean = tag.lower().strip()

        if tag_clean in JOB_ATTRIBUTES:
            job_attributes.append(tag)
        else:
            technical_skills.append(tag)

    return technical_skills, job_attributes

# SCRAPER FUNCTION

def scrape_remoteok(role, url):
    driver = get_driver()
    driver.get(url)
    time.sleep(5)

    # Safe scrolling
    for _ in range(NUM_SCROLLS):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE + random.uniform(0.5, 1.5))
        except Exception:
            print(" Browser closed unexpectedly. Stopping scroll.")
            break

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for job in soup.find_all("tr", class_="job"):
        title = job.find("h2")
        company = job.find("h3")
        location = job.find("div", class_="location")
        date_posted = job.find("time")
        href = job.get("data-href")

        # SKILLS EXTRACTION 
        
        skill_tags = job.select("td.tags h3")
        tags = [tag.get_text(strip=True) for tag in skill_tags if tag.get_text(strip=True)]

        technical_skills, job_attributes = classify_tags(tags)

        jobs.append({
            "Search Role": role,
            "Job Title": title.text.strip() if title else None,
            "Company Name": company.text.strip() if company else None,
            "Technical Skills": ", ".join(technical_skills) if technical_skills else None,
            "Job Attributes": ", ".join(job_attributes) if job_attributes else None,
            "Location": location.text.strip() if location else "Worldwide",
            "Date Posted": date_posted["datetime"] if date_posted else None,
            "Job URL": f"https://remoteok.com{href}" if href else None
        })

    return jobs

# MAIN EXECUTION

all_jobs = []

for role, url in JOB_ROLES.items():
    print(f"Scraping: {role}")
    try:
        role_jobs = scrape_remoteok(role, url)
        all_jobs.extend(role_jobs)
    except Exception as e:
        print(f"Failed for {role}: {e}")
    time.sleep(random.uniform(4, 7))

df = pd.DataFrame(all_jobs)
df.to_excel("remoteok_jobs_separated_skill2.xlsx", index=False)

print(df.head())
print(f"Total jobs scraped: {len(df)}")
