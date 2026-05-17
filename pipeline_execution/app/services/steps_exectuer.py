# ETL
# ☑ Remove Duplicates
# ☑ Fill Null Values
# ☑ Standardize Formats
# ELT Steps
# ☑ Load Raw Data
# ☑ SQL Transformation
# Batch Steps
# ☑ Batch Processing
# ☑ Batch Validation

import pandas as pd

# ETL STEPS
def remove_duplicates(df):
    return df.drop_duplicates()

def fill_null_values(df):
    for col in df.columns:
        if df[col].dtype=="object":
            df[col]=df[col].fillna("Unknown")
        else:
            df[col]=df[col].fillna(df[col].mean())
    return df

def standardize_formats(df):
    for col in df.select_dtypes(include='object'):
        df[col]=df[col].astype(str)
        df[col]=df[col].str.strip().str.lower()
    return df

# ELT STEPS
def load_raw_data(df):
    print("Loading raw data")
    return df

def  sql_transformations(df):
    print("Performing SQL transformations")
    return df

# Batch Steps
def batch_processing(df):
    print("Performing batch processing")
    return df

def batch_validation(df):
    print("Performing batch validation")
    return df


STEP_FUNCTIONS = {
    "remove_duplicates":remove_duplicates,
    "fill_null_values":fill_null_values,
    "standardize_formats":standardize_formats,
    "load_raw_data":load_raw_data,
    "sql_transformations":sql_transformations,
    "batch_processing":batch_processing,
    "batch_validation":batch_validation
}


def step_executer(df,steps):
    func= STEP_FUNCTIONS.get(steps)
    if func:
        return func(df)
    else:
        raise ValueError(f"Step {steps} not found")
    return df