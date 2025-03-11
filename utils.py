from bs4 import BeautifulSoup
import spacy
import re
import sqlite3
import pandas as pd
from transformers import pipeline
import requests


# Step 4: Financial Crime Classification
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
# Step 3: Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Step 1: Scrape News Articles
def scrape_news(url):
    """Scrape news articles from a given URL."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.text for p in paragraphs])
        return article_text
    else:
        return None

# Step 2: Preprocess Data
def preprocess_text(text):
    """Clean and preprocess the text."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    return text

def extract_entities(text):
    """Extract named entities (people, organizations)."""
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ["PERSON", "ORG"]]
    return entities




def classify_news(text):
    """Classify if the news is related to financial crime."""
    result = classifier(text[:512])  # Limit to first 512 characters
    return result[0]['label'], result[0]['score']



# Step 5: Store Data in SQLite
def store_data(article, entities, classification, confidence, source_url):
    conn = sqlite3.connect("financial_crime.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article TEXT, entities TEXT, classification TEXT, confidence REAL, source_url TEXT)
                   """
    )
    cursor.execute("INSERT INTO news (article, entities, classification, confidence, source_url) VALUES (?, ?, ?, ?, ?)",
                   (article, str(entities), classification, confidence, source_url))
    conn.commit()
    conn.close()