## Scraping

### Reuters

```bash
python reuters_newapi_scraper.py --query "economic offense" --out_path "./csv/reuters_economic_offense.csv"
```

### MAS

```bash
python mas_scraper.py
```

### News API

```bash
python news_api_articles.py --query "economic offense"
```

## LLM for summarization

### for SEC articles

```bash
python ollama_sec_summary.py
```

### For Reuters and new API articles

```bash
python ollama_reuters_newsapi_summary.py
```

## For Vector encoding and data collation

Look at the notebook `notebooks/FAISS.ipynb`
Look at the notebook `notebooks/ScraperData.ipynb` for collating the data from sources such as UNSC, reuters, etc.

## Frontend with streamlit and search retrieval with FAISS

```bash
streamlit run streamlit.py
```


