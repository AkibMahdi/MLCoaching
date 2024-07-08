from tqdm import tqdm
import requests
import time
from concurrent.futures import ThreadPoolExecutor


def fetch_article_ids(term, max_results=100000):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    params = {
        'db': 'pmc',
        'term': term,
        'retmax': max_results,
        'retmode': 'json'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data['esearchresult']['idlist']

article_ids = fetch_article_ids('cancer')
print(f"Fetched {len(article_ids)} article IDs.")

def fetch_article_metadata(article_id):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    params = {
        'db': 'pmc',
        'id': article_id,
        'retmode': 'xml'
    }
    response = requests.get(base_url, params=params)
    return response.text

def fetch_all_metadata(article_ids, max_workers=10):
    metadata_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for metadata in tqdm(executor.map(fetch_article_metadata, article_ids), total=len(article_ids)):
            metadata_list.append(metadata)
    return metadata_list

article_metadata_list = fetch_all_metadata(article_ids)
print(f"Fetched metadata for {len(article_metadata_list)} articles.")
