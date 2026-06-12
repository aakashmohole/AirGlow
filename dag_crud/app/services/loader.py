import os
import json
import pandas as pd
from sqlalchemy import text
from app.db.database import engine
from io import StringIO


def load_data(data, destination_config):
    destination_type = destination_config.get("type")

    if destination_type == "csv":
        file_path = destination_config.get("file_path")

        if not file_path:
            raise Exception("File path is required for csv destination")
        
        os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
        )


        df= pd.DataFrame(data)
        buffer = StringIO()
        df.to_csv(buffer, index=False)

        return{
            "status": "success",
            "file_name":"users.csv",
            "content": buffer.getvalue(),
            "file_type":"csv",
            "rows": len(df)
        }
        
    elif destination_type == "json":
        file_path = destination_config.get("file_path")
        if not file_path:
            raise Exception("File path is required for csv destination")
        
        os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
        )

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        return{
            "status": "success",
            "file_name":"users.json",
            "file_path":buffer.getvalue(),
            "file_type":"json",
            "rows": len(data) 
        }
    
    elif destination_type == "db":
        table_name = destination_config.get("table")

        if not table_name:
            raise Exception("Table is required for DB destination")

        df= pd.DataFrame(data)
        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False
        )

        return{
            "status":"success",
            "file_name":None,
            "file_path":None,
            "file_type":"db",
            "rows":len(df)
        }
    
    else:
        raise Exception(
            f"Unsupported destination type : {destination_type}")
        