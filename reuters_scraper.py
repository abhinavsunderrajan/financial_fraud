from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crewai_tools import ScrapeWebsiteTool
import argparse
import time
import random
import pandas as pd
import glob
from tqdm import tqdm
if __name__ == "__main__":
    """
    This script is used to scrape the text and URLs of the articles from the Reuters search page.
    It will save the results to a CSV file. 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="the query to search for")
    args = parser.parse_args()
    query = args.query

   
    driver = webdriver.Chrome()  # Ensure the ChromeDriver is in your PATH
   
    # Extract and print the text and URLs
    link_text_ls = []
    link_url_ls = []
    # Open the Reuters search page and proceed to next few pages to get more articles
    try:
        url = f"https://www.reuters.com/site-search/?query={query.replace(' ','+')}"
        driver.get(url)
        
        # Wait for elements to be present
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="TitleLink"]'))
        )
        
        
        for element in elements:
            link_text = element.get_attribute('aria-label')
            link_url = element.get_attribute('href')
            # print(f"Link Text: {element.text}")
            # print(f"Link URL: {link_url}")
            link_text_ls.append(element.text)
            link_url_ls.append(link_url)

        driver.quit()
        for page in range(2, 5):
            # Wait for the "Next" button to be present and clickable
            print("click next button")
            time.sleep(random.uniform(2, 5))
            driver = webdriver.Chrome()
            driver.get(f"{url}&offset={page*10}")

        # Optionally, wait for the page to load and perform further actions
            # For example, wait for new page content to load
            elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="TitleLink"]'))
            )
            print(len(elements))

            for element in elements:
                link_text = element.get_attribute('aria-label')
                link_url = element.get_attribute('href')
                link_text_ls.append(element.text)
                link_url_ls.append(link_url)

            
    finally:
        # Close the browser
        driver.quit()

    if len(link_text_ls)>0:
        result_df = pd.DataFrame({"link_text":link_text_ls, "link_url": link_url_ls})
        print(len(result_df))
        result_df.to_csv(f"./csv/reuters_{query}.csv", index=False)

    reuters_files = glob("./csv/reuters_*.csv")
    reuters_articles = pd.concat([(pd.read_csv(file)) for file in reuters_files], ignore_index=True)
    print(len(reuters_articles))
    # To enable scrapping any website it finds during it's execution
    tool = ScrapeWebsiteTool()
    article_text_ls = []

    for index_, row in tqdm(reuters_articles.iterrows()):

        tool = ScrapeWebsiteTool(website_url=row["link_url"])
        # Extract the text from the site
        text = tool.run()
        article_text_ls.append(text)

    reuters_articles["article"] = article_text_ls
    reuters_articles.to_csv("./csv/all_reuters_scraped.csv", index=False)