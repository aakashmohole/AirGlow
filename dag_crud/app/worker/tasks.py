from datetime import datetime
from app.worker.celery_app import celery
from app.db.database import SessionLocal
from app.models.dag_runs import DAGRun
from app.models.dag import DAG
from app.core.executor import execute_pipeline

@celery.task(name="app.worker.tasks.run_dag")
def run_dag(dag_id, run_id):
    db = SessionLocal()
    try:
        dag = db.query(DAG).filter(DAG.id == dag_id).first()
        run = db.query(DAGRun).filter(DAGRun.id == run_id).first()

        if run:
            run.status = "running"
            run.start_time = datetime.utcnow()
            db.commit()

        execute_pipeline(
            dag_type=dag.dag_type,
            source_config=dag.source_config,
            destination_config=dag.destination_config,
            transform_config=dag.transform_config
        )

        if run:
            run.status = "success"
            run.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        if run:
            run.status = "failed"
            run.end_time = datetime.utcnow()
            db.commit()
        raise e
    finally:
        db.close()
