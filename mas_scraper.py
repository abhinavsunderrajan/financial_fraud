import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm
from pandarallel import pandarallel
pandarallel.initialize(nb_workers = 16, progress_bar=True)

def get_all_mass_offenses(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    text = re.sub(r'\n+', '\n', text.strip("\t"))
    return re.sub(r' +', ' ', text.strip("\t")).strip()

if __name__ == "__main__":
    """
    This script is used to scrape the text and URLs of the articles from the MAS enforcement actions page.
    It will save the results to a CSV file. 
    """

    website = 'https://www.mas.gov.sg'
    url = 'https://www.mas.gov.sg/regulation/enforcement/enforcement-actions/?page=1&q=&sort=&rows=All#MasXbeEnforcementActionKeyword'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find_all('table')

    # Extract headers
    headers = [header.get_text(strip=True) for header in table[0].find_all('th')]
    headers.append('url_link')

    # Extract rows
    rows = []
    for row in table[0].find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        row_data = []
        for cell in cells:
            row_data.append(cell.get_text(strip=True))
            if cell.find('a', href=True) is not None:
                row_data.append(cell.find('a', href=True) ['href'])
        rows.append(row_data)

    # Create a pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
    df["url_link"] = df["url_link"].apply(lambda x: f"{website}{x}")

    df["economic_offense"] = df.parallel_apply(lambda row: get_all_mass_offenses(row['url_link']), axis=1)
    df.to_csv("mas_enforcement_actions.csv", index=False)
