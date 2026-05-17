import pandas as pd
import requests

def read_api(url):
    try:
        response=requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error reading API: {e}")
        return None