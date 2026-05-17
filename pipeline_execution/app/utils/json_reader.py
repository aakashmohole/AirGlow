import pandas as pd

def read_json(file_path):
    try:
        df = pd.read_json(file_path)
        return df
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None