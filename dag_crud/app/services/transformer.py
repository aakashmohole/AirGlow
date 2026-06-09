import json

def transform_data(data , transformation_config):
    for rule in transformation_config or []:

        if rule.get("type")=="remove_duplicates":
            seen = set()
            deduplicated = []
            for d in data:
                serialized = json.dumps(d, sort_keys=True)
                if serialized not in seen:
                    seen.add(serialized)
                    deduplicated.append(d)
            data = deduplicated

        if rule.get("type")=="fill_null":
            col= rule["column"]
            value= rule.get("value", 0)

            for row in data:
                if row.get(col) is None:
                    row[col] = value
            
    return data