from app.services.steps_exectuer import step_executer as execute_step

def run_pipeline(df,steps):
    for step in steps:
        print(f"Running Step: {step}")
        df=execute_step(df,step)
    return df