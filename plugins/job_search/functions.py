import os
import requests

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_jobs(query: str, num_results: int = 10):
    """
    Search for job listings using Google Custom Search API.
    
    :param query: The job search query
    :param num_results: Number of results to return (default: 10)
    :return: A list of job listings
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": num_results
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    
    items = response.json().get("items", [])
    legitimate_jobs = [item for item in items if is_legitimate_job_site(item['link'])]
    return legitimate_jobs[:num_results]

def is_legitimate_job_site(url: str) -> bool:
    """
    Check if a given URL is likely to be a legitimate job listing site.
    
    :param url: The URL to check
    :return: True if the site appears to be a legitimate job site, False otherwise
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            job_keywords = ["job", "career", "employment", "hiring", "vacancy"]
            return any(keyword in response.text.lower() for keyword in job_keywords)
    except:
        pass
    return False