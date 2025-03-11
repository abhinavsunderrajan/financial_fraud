from glob import glob
import random
from pydantic import BaseModel
import asyncio
from ollama import AsyncClient
import json
from tqdm import tqdm
import os
import pandas as pd

class ArticleSummary(BaseModel):
    article_category: str
    people_mentioned: list[str]
    country: list[str]
    summary: str



async def chat(message):
    response = await AsyncClient().chat(
    model='llama3.1', format=ArticleSummary.model_json_schema(), 
    options={'temperature': 0},messages=[{'role': 'user', 'content': message}])
    return response

if __name__ == '__main__':

    question = """Based on the content of the article, can you extract the following information. 
    1. Extract the article category into one of the following: 'Financial Scam', 'Money laundering', 'Terror Financing' or 'Other'. Restrict the category to these four only.
    2. Extract only the people or entities mentioned in the article who are involved in the fraud/scam/money laundering. 
    3. Extract the country the people or entities are from. 
    4. Summarize the article in less than 300 words.
    Return the answer as a json with four fields article_category, people_mentioned, country and summary.
    """
    csv_files = ["/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/csv/all_newsapi_scraped.csv",
                 "/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/csv/all_reuters_scraped.csv"]
    df = pd.concat([pd.read_csv(file)[['link_url', 'article']] for file in csv_files], ignore_index=True)
    print("Number of articles: ", len(df))
    write_dir = '/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/reuter_newsapi_json'
    for index, row in tqdm(df.iterrows()):
        file = row['link_url'].split("/")[-1]
        if len(file) ==0:
            file = row['link_url'].split("/")[-2]

        if os.path.exists(f'{write_dir}/{file}.json'):
            continue
        if len(file) >50:
            file = file[:50]
        
        text = row['article']
        response = asyncio.run(chat(question + '\n\n' + text))
        response_data = json.loads(response.message.content)
        sec_summary = ArticleSummary.model_validate(response_data)
        with open(f'{write_dir}/{file.split("/")[-1]}.json', 'w') as f:
            json.dump(sec_summary.model_dump(), f,indent=4)