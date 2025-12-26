# scrape_jobs.py -- OPTIONAL Selenium scraper (example). Use responsibly and respect Terms of Service.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time, sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'jobs.db')

def save_job(conn, job):
    c = conn.cursor()
    c.execute('INSERT INTO jobs (source,title,company,location,description,url) VALUES (?,?,?,?,?,?)', (job['source'], job['title'], job.get('company'), job.get('location'), job.get('description'), job.get('url')))
    conn.commit()

def scrape_indeed(query='machine+learning'):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = f'https://in.indeed.com/jobs?q={query}'
    driver.get(url)
    time.sleep(3)
    cards = driver.find_elements(By.CSS_SELECTOR, 'a')[:15]
    results = []
    for c in cards:
        try:
            title = c.text
            href = c.get_attribute('href')
            if title and href and 'jk=' in (href or ''):
                results.append({'source':'indeed','title':title,'company':None,'location':None,'description':'','url':href})
        except:
            pass
    driver.quit()
    return results

if __name__ == '__main__':
    print('This script demonstrates how to scrape job listings. Use responsibly. It requires Chrome and ChromeDriver.')