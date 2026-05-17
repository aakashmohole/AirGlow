PIPELINE_STEPS = {
    "etl":[
        {
            "name":"remove_duplicates",
            "label":"Remove Duplicates"
        },
        {
            "name":"fill_null_values",
            "label":"Fill Null Values"
        },
        {
            "name":"staandardize_formats",
            "label":"Standardize Formats"
        }
    ],
    "elt":[
        {
            "name":"load_raw_data",
            "label":"Load Raw Data"
        },
        {
            "name":"sql_transformations",
            "label":"SQL Transformations"
        }
    ],
    "batch":[
        {
            "name":"batch_processing",
            "label":"Batch Processing"
        },
        {
            "name":"batch_validation",
            "label":"Batch Validation"
        }
    ]
}