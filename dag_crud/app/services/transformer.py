def transform_data(data , rules):
    for rule in rules or []:
        if rule["type"]=="remove_duplicates":
            data = [dict(t) for t in {tuple(d.items()) for d in data}]

        if rule["type"]=="fill_null":
            col= rule["column"]
            value= rule.get("value", 0)

            for row in data:
                if row.get(col) is None:
                    row[col] = value
            
    return data