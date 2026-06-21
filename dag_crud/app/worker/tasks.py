from datetime import datetime
from app.worker.celery_app import celery
from app.db.database import SessionLocal
from app.models.dag_runs import DAGRun
from app.models.dag import DAG
from app.services.extractor import extract_data
from app.services.transformer import transform_data
from app.models.output_file import OutputFile
from app.services.loader import load_data
from croniter import croniter
from app.core.webhook_sender import send_webhook
from app.models import Webhook




@celery.task(name="app.worker.tasks.run_dag",
            autoretry_for=(Exception,),
            retry_kwargd={"max_retries":3, "countdown":30})
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

        # load_result= load_data(
        #     transformed_data,
        #     dag.destination_config
        # )
        load_result = {
            "file_name":"users.json",
            "file_type":"json",
            "content":transformed_data,
            "rows":len(transformed_data)
        }
        output_file = OutputFile(
            dag_id=dag.id,
            run_id=run.id,
            file_name=load_result["file_name"],
            content = load_result["content"],
            file_type = load_result["file_type"],
            records_count=load_result["rows"]
            )
        db.add(output_file)
        db.commit()



        if run:
            run.status = "success"
            run.end_time = datetime.utcnow()

            run.log={
                "dag_type": dag.dag_type,
                "source": dag.source_config,
                "destination": dag.destination_config,
                "records_extracted": records_extracted,
                "records_transformed": records_transformed,
                "records_loaded":load_result["rows"],
                "output_file": load_result["file_name"],
                "message": "DAG executed successfully"
            }
            db.commit()



        start = datetime.utcnow()
        end = datetime.utcnow()
        run.execution_time= (end-start).total_seconds()
        run.records_extracted = records_extracted
        run.records_transformed = records_transformed
        run.records_loaded = load_result["rows"]

    except Exception as e:
        db.rollback()
        if run :
            run.status = "failed"
            run.end_time = datetime.utcnow()
            run.log={"error": str(e)}
            db.commit()
    finally:
            db.close()

   

def is_dag_due(dag):
    
    if dag.scheduler_type == "manual":
        return False
    if dag.scheduler_type == "cron":
        cron = dag.cron_expression
        if not cron:
            return False
        now = datetime.utcnow()
        previous_run = croniter(
            cron, now
        ).get_prev(datetime)

        diff=(
            now-previous_run
        ).total_seconds()
        return diff < 60
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


send_webhook(
    Webhook.callback_url,
    {
        "dag_id": DAG.dag_id,
        "status": "success"
    }
)