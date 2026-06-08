import pandas as pd
import requests

def read_csv(file_path):
    return pd.read_csv(file_path)

def read_json(file_path):
    return pd.read_json(file_path)

def read_api(api_url):
    response = requests.get(api_url)
    data = response.json()
    return pd.DataFrame(data)

