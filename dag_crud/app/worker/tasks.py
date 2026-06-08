from datetime import datetime
from app.worker.celery_app import celery
from app.db.database import SessionLocal
from app.models.dag_runs import DAGRun
from app.models.dag import DAG
 
from app.services.loader import load_data
from app.services.transformer import transform_data
from app.services.extractor import extract_data



@celery.task
def run_dag(dag_id, run_id):
    db= SessionLocal()
    try:
        dag=db.query(DAG).filter(DAG.id==dag_id).first()
        run=db.query(DAGRun).filter(DAGRun.id==run_id).first()

        run.status="running"
        run.start_time=datetime.utcnow()
        db.commit()

        data= extract_data(dag.source_config)
        transformed_data= transform_data(data, dag.transformations)
        load_data(transformed_data, dag.destination_config)

        run.status="success"
        run.end_time=datetime.utcnow()
        db.commit()

    except Exception as e:
        run.status="failed"
        run.end_time=datetime.utcnow()
        run.log={"error": str(e)}
        db.commit()
    finally:
        db.commit()
        db.close()
