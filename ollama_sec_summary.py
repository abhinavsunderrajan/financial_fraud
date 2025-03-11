from glob import glob
import random
from pydantic import BaseModel
import asyncio
from ollama import AsyncClient
import json
from tqdm import tqdm
import os

class SecFraudSummary(BaseModel):
    litigants: list[str]
    country: list[str]
    summary: str


async def chat(message):
    response = await AsyncClient().chat(
    model='llama3.1', format=SecFraudSummary.model_json_schema(), 
    options={'temperature': 0},messages=[{'role': 'user', 'content': message}])
    return response

if __name__ == '__main__':

    text_files = glob('/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/sec_text/*.txt')
    write_dir = '/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/sec_json'

    question = """Based on the content below can you three tasks. 
    1. Extract all the litigants
    2. Extract the country the litigants are from. 
    3. Summarize the nature of the fraud in less than 200 words.
    Return the answer as a json with three fields name litigants, country and summary.
    """

    for file in tqdm(text_files):
        if os.path.exists(f'{write_dir}/{file.split("/")[-1]}.json'):
            continue
        with open(file, 'r') as f:
            text = f.read()
        response = asyncio.run(chat(question + '\n\n' + text))
        response_data = json.loads(response.message.content)
        sec_summary = SecFraudSummary.model_validate(response_data)
        with open(f'{write_dir}/{file.split("/")[-1]}.json', 'w') as f:
            json.dump(sec_summary.model_dump(), f,indent=4)



# response = ollama.chat(
#     model='llama3.2-vision',
#     messages=[{
#         'role': 'user',
#         'content': 'Can you describe the man in the image?',
#         'images': ['/Users/abhinav.sunderrajan/Downloads/AbhinavPhoto.jpg']
#     }]
# )