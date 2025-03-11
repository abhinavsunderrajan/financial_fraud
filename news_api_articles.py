from newsapi import NewsApiClient
import pandas as pd
import requests
import json
import argparse
from bs4 import BeautifulSoup
from tqdm import tqdm
from crewai_tools import ScrapeWebsiteTool
import dotenv
from glob import glob
import os
dotenv.load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="the query to search for")
    args = parser.parse_args()
    query = args.query
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

    all_articles = newsapi.get_everything(q=query,
                                      from_param='2025-03-03',
                                      to='2025-01-01',
                                      # sources = 'the-wall-street-journal',
                                      language='en',
                                      page=5,
                                      sort_by='popularity')
    print(len(all_articles['articles']))
    if len(all_articles['articles']) >0:
        pd.DataFrame(all_articles['articles']).to_csv(f"./csv/query_{query}.csv", index=False)

    # get the new API articles links for all queries and scrape the text
    newsapi_files = glob("./csv/query_*.csv")
    newsapi_files_articles = pd.concat([(pd.read_csv(file)) for file in newsapi_files], ignore_index=True)

    news_api_text = []

    for index_, row in tqdm(newsapi_files_articles.iterrows()):
        try:
            tool = ScrapeWebsiteTool(website_url=row["url"])
            # Extract the text from the site
            text = tool.run()
            news_api_text.append(text)
        except Exception as e: 
            print(e)
            news_api_text.append("")

    newsapi_files_articles["article"] = news_api_text
    newsapi_files_articles = newsapi_files_articles.loc[newsapi_files_articles.article.str.len()>0]
    newsapi_files_articles.to_csv("./csv/all_newsapi_scraped.csv", index=False)