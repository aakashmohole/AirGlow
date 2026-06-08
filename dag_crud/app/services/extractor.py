import requests
import pandas as pd
import json

def extract_data(source_config):
    if source_config["type"] == "api":
      return requests.get(source_config["url"]).json()
   
    if source_config["type"] == "csv":
      df= pd.read_csv(source_config["file_path"])
      return df.to_dict(orient="records")
   
    if source_config["type"] == "json_file":
        with open(source_config["file_path"], "r") as f:
            data = json.load(f)
        return data

    if source_config["type"] == "json_string":
        return json.loads(source_config["data"])

    return []