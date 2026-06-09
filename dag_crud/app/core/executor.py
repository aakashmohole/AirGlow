from app.services.extractor import extract_data
from app.services.transformer import transform_data
from app.services.loader import load_data

def execute_pipeline(dag_type, source_config, destination_config, transform_config):

    data = None

    if dag_type == 'ETL':
        data = extract_data(source_config)
        transformed_data = transform_data(data, transform_config)
        load_data(transformed_data, destination_config)

    elif dag_type == 'ELT':
        data= extract_data(source_config)
        load_data(data, destination_config)
        transform_data(data, transform_config)

    elif dag_type == 'BATCH':
        batch_data = extract_data(source_config)
        for chunk in batch_data:
            transformed_chunk = transform_data(chunk, transform_config)
            load_data(transformed_chunk, destination_config)

    return True