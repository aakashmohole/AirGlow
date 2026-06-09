
import json


def load_data(data, destination_config):
    if destination_config["type"] == "memory":
        
        return data 
    elif destination_config["type"] == "print":
        print(data)

    print(f"Loading data into : {destination_config}")
    return True