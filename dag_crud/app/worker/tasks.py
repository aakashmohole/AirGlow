from datetime import datetime
from app.worker.celery_app import celery
from app.db.database import SessionLocal
from app.models.dag_runs import DAGRun
from app.models.dag import DAG
from app.services.extractor import extract_data
from app.services.transformer import transform_data
from app.services.loader import load_data


@celery.task(name="app.worker.tasks.run_dag")
def run_dag(dag_id, run_id):
    db = SessionLocal()
    try:
        dag = db.query(DAG).filter(DAG.id == dag_id).first()
        run = db.query(DAGRun).filter(DAGRun.id == run_id).first()

        if not dag:
            raise Exception(f"DAG with id {dag_id} not found")
        
        if run:
            run.status = "running"
            run.start_time = datetime.utcnow()
            db.commit()

        data = extract_data(dag.source_config)
        records_extracted=len(data) if isinstance(data, list) else 1

        transformed_data = transform_data(
            data,
            dag.transform_config
        )
        records_transformed= len(transformed_data) if isinstance(transformed_data, list) else 1

        load_data(transformed_data, dag.destination_config)

        if run:
            run.status = "success"
            run.end_time = datetime.utcnow()

            run.log={
                "dag_type": dag.dag_type,
                "source": dag.source_config,
                "destination": dag.destination_config,
                "records_extracted": records_extracted,
                "records_transformed": records_transformed,
                "message": "DAG executed successfully"
            }
            db.commit()

    except Exception as e:
        if run :
            run.status = "failed"
            run.end_time = datetime.utcnow()
            run.log={"error": str(e)}
            db.commit()
    finally:
            db.close()

   



def is_dag_due(dag):
    scheduler = str(dag.scheduler).lower()

    if dag.scheduler == "manual":
        return False
    if dag.scheduler == "hourly":
        return True
    if dag.scheduler == "daily":
        return True
    if ":" in str(dag.scheduler):
        now = datetime.utcnow().strftime("%H:%M")
        return now == dag.scheduler
    
    return False


@celery.task
def scan_and_trigger_dags():
    db = SessionLocal()
    try:
        dags = db.query(DAG).all()
        for dag in dags:
            if is_dag_due(dag):
                run = DAGRun(dag_id=dag.id, status="queued")
                db.add(run)
                db.commit()
                db.refresh(run)
                run_dag.delay(dag.id, run.id)
    finally:
        db.close()