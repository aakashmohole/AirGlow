from app.services.steps_exectuer import step_executer as execute_step
from app.utils.data_reader import (
    read_api, read_csv,read_json
)

def run_pipeline(pipeline):
    source_type= pipeline.source_type
    source_config= pipeline.source_config
    transform_config=pipeline.transform_config

    if source_type == "csv":
        df= read_csv(
            source_config["file_path"]
        )
    elif source_type == "json":
        df = read_json(
            source_config["file_path"]
        )
    elif source_type == "api":
        df=read_api(
            source_config["api_url"]
        )
    else :
        return Exception("Invalid Source Type")




    steps = transform_config["steps"]

    for step in steps:

        print(f"Running Step: {step}")

        df = execute_step(df, step)


    return df