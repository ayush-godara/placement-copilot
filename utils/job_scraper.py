"""
Job Scraper — Multi-platform scraper for Internshala, Naukri, and startup job boards.
Uses requests + BeautifulSoup.
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_internshala(query: str = "software developer", location: str = "", page: int = 1, is_internship: bool = True) -> list[dict]:
    """Scrape Internshala for internship listings."""
    jobs = []
    try:
        # If they want jobs, append "job" to query if not present, though internshala is mainly internships
        query_slug = query.lower().replace(" ", "-")
        if not is_internship and "job" not in query_slug:
            query_slug += "-job"
            
        if location:
            loc_slug = location.lower().replace(" ", "-")
            url = f"https://internshala.com/internships/{query_slug}-internship-in-{loc_slug}/page-{page}" if is_internship else f"https://internshala.com/jobs/{query_slug}-jobs-in-{loc_slug}/page-{page}"
        else:
            url = f"https://internshala.com/internships/{query_slug}-internship/page-{page}" if is_internship else f"https://internshala.com/jobs/{query_slug}-jobs/page-{page}"

        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".individual_internship, .internship_meta, [class*='individual_internship']")
        if not cards:
            cards = soup.select(".internship-heading-container, .container-fluid.individual_internship")

        for card in cards[:25]:
            try:
                title_el = card.select_one(".heading_4_5 a, .job-internship-name, h3 a, .profile a")
                title = title_el.get_text(strip=True) if title_el else ""
                company_el = card.select_one(".heading_6, .company-name, h4 a, .company_name a")
                company = company_el.get_text(strip=True) if company_el else ""
                loc_el = card.select_one(".location_link, #location_names, .locations a")
                loc = loc_el.get_text(strip=True) if loc_el else "Remote"
                
                # Extract Stipend
                stipend_el = card.select_one(".stipend, .salary, span.stipend")
                stipend = stipend_el.get_text(strip=True) if stipend_el else ""
                
                link_el = title_el if title_el and title_el.get("href") else card.select_one("a[href*='internship/detail'], a[href*='job/detail']")
                href = ""
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    if not href.startswith("http"):
                        href = f"https://internshala.com{href}"
                        
                if title and company:
                    jobs.append({"title": title, "company": company, "location": loc, "url": href, "description": stipend, "source": "Internshala"})
            except Exception:
                continue
    except Exception:
        pass
    return jobs


def scrape_naukri(query: str = "software developer", location: str = "", experience: str = "0", is_internship: bool = False) -> list[dict]:
    """Scrape Naukri.com for job/internship listings."""
    jobs = []
    try:
        if is_internship and "intern" not in query.lower():
            query += " internship"
            
        query_slug = query.lower().replace(" ", "-")
        url = f"https://www.naukri.com/{query_slug}-jobs"
        if location:
            url += f"-in-{location.lower().replace(' ', '-')}"
        url += f"?experience={experience}"

        response = requests.get(url, headers={**HEADERS, "Referer": "https://www.naukri.com/"}, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".srp-jobtuple-wrapper, .jobTuple, article.jobTuple")
        if not cards:
            cards = soup.select("[class*='jobTuple'], [class*='cust-job-tuple']")

        for card in cards[:25]:
            try:
                title_el = card.select_one(".title, .jobTitle a, a.title")
                title = title_el.get_text(strip=True) if title_el else ""
                company_el = card.select_one(".comp-name, .companyInfo a, .subTitle a")
                company = company_el.get_text(strip=True) if company_el else ""
                loc_el = card.select_one(".locWdth, .location, .loc span")
                loc = loc_el.get_text(strip=True) if loc_el else ""
                
                # Extract Salary/Stipend
                salary_el = card.select_one(".salary, .sal, li.salary span")
                salary = salary_el.get_text(strip=True) if salary_el else ""
                
                href = ""
                if title_el and title_el.get("href"):
                    href = title_el["href"]
                if title and company:
                    jobs.append({"title": title, "company": company, "location": loc, "url": href, "description": salary, "source": "Naukri"})
            except Exception:
                continue
    except Exception:
        pass
    return jobs


def scrape_linkedin(query: str = "software developer", location: str = "", is_internship: bool = False) -> list[dict]:
    """Scrape LinkedIn public job listings."""
    jobs = []
    try:
        if is_internship and "intern" not in query.lower():
            query += " internship"
            
        url = f"https://www.linkedin.com/jobs/search?keywords={requests.utils.quote(query)}"
        if location:
            url += f"&location={requests.utils.quote(location)}"

        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".base-search-card")

        for card in cards[:25]:
            try:
                title_el = card.select_one(".base-search-card__title")
                title = title_el.get_text(strip=True) if title_el else ""
                company_el = card.select_one(".base-search-card__subtitle")
                company = company_el.get_text(strip=True) if company_el else ""
                loc_el = card.select_one(".job-search-card__location")
                loc = loc_el.get_text(strip=True) if loc_el else ""
                
                salary_el = card.select_one(".job-search-card__salary-info")
                salary = salary_el.get_text(strip=True) if salary_el else ""
                
                href = ""
                link_el = card.select_one(".base-card__full-link")
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    
                if title and company:
                    jobs.append({"title": title, "company": company, "location": loc, "url": href, "description": salary, "source": "LinkedIn"})
            except Exception:
                continue
    except Exception:
        pass
    return jobs


def scrape_all_platforms(query: str, location: str = "", is_internship: bool = False) -> list[dict]:
    """Scrape all platforms and deduplicate results."""
    all_jobs = []

    # Internshala - multiple pages
    for page in range(1, 3):
        all_jobs.extend(scrape_internshala(query, location, page, is_internship))

    # Naukri
    all_jobs.extend(scrape_naukri(query, location, "0", is_internship))
    
    # LinkedIn
    all_jobs.extend(scrape_linkedin(query, location, is_internship))

    # Deduplicate by company+title
    seen = set()
    unique = []
    for job in all_jobs:
        key = (job["company"].lower(), job["title"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique
