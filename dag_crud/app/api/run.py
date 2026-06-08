from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.worker.tasks import run_dag
from app.models.dag_runs import DAGRun

router = APIRouter(prefix="/dags", tags=["Executions"])

@router.post("/{dag_id}/run")
def run_pipeline(dag_id: int, db: Session = Depends(get_db)):

    dag_run = DAGRun(dag_id=dag_id, status="queued")
    db.add(dag_run)
    db.commit()
    db.refresh(dag_run)

    run_dag.delay(dag_id,dag_run.id)

    return {"message": f"DAG {dag_id} execution started", "run_id": dag_run.id}