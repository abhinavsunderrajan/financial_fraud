from bs4 import BeautifulSoup
import pandas as pd
import time
from glob import glob
import ast
from tqdm import tqdm
import os
import string
from tqdm import tqdm
from crewai_tools import ScrapeWebsiteTool
from selenium.webdriver.support.ui import WebDriverWait
import xml.etree.ElementTree as ET

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_page_details(url, driver):
    base_name = url.split("populate=")[-1].replace("&", "_").replace("=", "_")
    file_path = f"./sec_data/sec_data{base_name}.csv"
    if os.path.exists(file_path):
        # print(f"Finished {url}")
        return

    driver.get(url)
    time.sleep(1)  # Allow time for page to load
    
    # Find the table containing litigation releases
    try:
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        # Extract headers
        headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
    
        # Extract data from rows
        data = []
        for row in rows[1:]:  # Skip header row
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = [col.text.strip() for col in cols]
            # Extract hyperlink from the first column (if present)
            # print(cols[1].text)
            links = cols[1].find_elements(By.TAG_NAME, "a")
            links = [link.get_attribute("href") for link in links]
            
    
            row_data.append(links)  # Add link as the last column
            data.append(row_data)
    
        # Append "Link" column to headers
        headers.append("Link")
    
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(file_path, index=False)
        driver.quit()
        print(f"Completed file of {len(df)} for {url}")
    except Exception as e:
        print(f"❌ Error scraping table for:  {url}")
        driver.quit()
        
if __name__ == "__main__":
    #configure Selenium with Chrome (Headless Mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    # get the table of all SEC litigations
    sec_year_month = pd.DataFrame({"year" : list(range(1996, 2026))})
    sec_year_month["month"] = [list(range(1, 13)) for i in range(len(sec_year_month))]
    sec_year_month = sec_year_month.explode("month")
    sec_year_month.reset_index(inplace=True, drop=True)
    sec_year_month["page_url"] = sec_year_month.apply(lambda row: f"https://www.sec.gov/enforcement-litigation/litigation-releases?populate=&year={row['year']}&month={row['month']}", axis=1)
    sec_year_month = sec_year_month.iloc[:-10]

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    sec_year_month.apply(lambda row: get_page_details(row['page_url']),axis=1)


    all_lits = [pd.read_csv(file) for file in glob("./sec_data/*csv")]
    all_lits_sec = pd.concat(all_lits, ignore_index=True)
    print(len(all_lits_sec))
    all_lits_sec["year"] = all_lits_sec["Date\nSort descending"].apply(lambda x: int(x.split(',')[1].strip()))
    all_lits_sec = all_lits_sec.sort_values(by=["year"], ascending=False)
    all_lits_sec.reset_index(inplace=True, drop=True)

    # once the table is scraped, scrape the text of the litigations
    for index_, row in tqdm(all_lits_sec.iterrows()):
        try:
            respondents = row["Respondents"].replace('\n', ' ')
            respondents = respondents.translate(str.maketrans('', '', string.punctuation))
            links = row["Link"]
            date = row["Date\nSort descending"]
            links = ast.literal_eval(links)
            # print(links, type(links))
            
            for i, link in enumerate(links):
                file_name = f"./sec_text/{date}_{respondents.split(',')[0][:15]}_link_{i}.txt"
                if os.path.exists(file_name) or ".pdf" in link:
                    continue
                driver.get(link)
                # time.sleep(1)  # Allow time for page to load   
                title = driver.title.strip()
                # Extract full page content
                full_content = driver.find_element("tag name", "body").text.strip()
                f = open(file_name, "a")
                f.write(full_content)
                f.close()
        except Exception as e:
            continue
    