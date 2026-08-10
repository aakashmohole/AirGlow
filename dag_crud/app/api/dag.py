from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.dag import DAG
from app.schemas.dag import DAGCreate, DAGResponse, DAGUpdate
from app.db.dependencies import get_db
from app.models.dag_runs import DAGRun
from app.models.output_file import OutputFile
from fastapi.responses import Response
import json
import pandas as pd
from croniter import croniter
from app.core.auth import get_current_user
from fastapi import Request
from app.core.rate_limiting import limiter


router=APIRouter(prefix="/dags",tags=["DAGs"])


@router.post("/", response_model=DAGResponse)
@limiter.limit("20/minute")
def create_dag(
    request : Request,
    payload: DAGCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.scheduler_type == "auto":
        if not payload.cron_expression:
            raise HTTPException(
                status_code=400,
                detail="cron_expression is required for auto scheduler"
            )

        if not croniter.is_valid(payload.cron_expression):
            raise HTTPException(
                status_code=400,
                detail="Invalid cron expression"
            )

    dag = DAG(
        **payload.dict(),
        user_id=int(current_user["sub"])
    )
    print("CURRENT USER:", current_user)
    print(type(current_user))

    db.add(dag)
    db.commit()
    db.refresh(dag)


    return dag


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user



@router.get("/", response_model=list[DAGResponse])
def get_dags(
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db)):
    return db.query(DAG).filter(
        DAG.user_id == current_user["sub"]
    ).all()
    



@router.get("/{dag_id}", response_model=DAGResponse)
def get_dag(dag_id:int, db:Session=Depends(get_db)):
    dag=db.query(DAG).filter(DAG.id==dag_id).first()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG Not Found")
    
    return dag


@router.put("/{dag_id}", response_model=DAGResponse)
def update_dag(dag_id:int, payload:DAGUpdate, db:Session=Depends(get_db)):
    dag=db.query(DAG).filter(DAG.id==dag_id).first()

    if not dag:
        raise HTTPException(status_code=404, detail="DAG Not Found")
    
    dag.dag_name=payload.dag_name
    dag.dag_type=payload.dag_type
    dag.scheduler_type=payload.scheduler_type
    dag.cron_expression=payload.cron_expression
    dag.source_config=payload.source_config
    dag.transform_config=payload.transform_config
    dag.destination_config=payload.destination_config   

    db.commit()
    db.refresh(dag)
    return dag


@router.delete("/{dag_id}")
def delete_dag(dag_id:int, db:Session=Depends(get_db)):
    dag=db.query(DAG).filter(DAG.id==dag_id).first()

    if not dag:
        raise HTTPException(status_code=404, detail="DAG Not Found")
    
    db.query(DAGRun).filter(
        DAGRun.dag_id==dag_id
    ).delete()
    
    db.delete(dag)
    db.commit()
    return {"Message":"DAG Deleted Successfully"}



@router.get("/{dag_id}/download")
def download_file(
    dag_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dag = db.query(DAG).filter(
        DAG.id == dag_id,
        DAG.user_id == current_user["sub"]
    ).first()

    if not dag:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this DAG"
        )

    file = (
        db.query(OutputFile)
        .filter(OutputFile.dag_id == dag_id)
        .order_by(OutputFile.id.desc())
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="No output found for this DAG"
        )

    # Existing JSON/CSV/DB logic

    elif file.file_type == "csv":
        df = pd.DataFrame(file.content)

        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv",
            headers={
                "Content-Disposition":
                f'attachment; filename="{file.file_name}"'
            }
        )

    elif file.file_type == "db":
        return {
            "message": "Data stored in database",
            "records": file.records_count,
            "data": file.content
        }

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type"
    )

@router.get("/{dag_id}/runs")
def get_runs(dag_id:int, db:Session=Depends(get_db)):
    return(
        db.query(DAGRun).filter(DAGRun.dag_id==dag_id)
        .order_by(DAGRun.created_at.desc())
        .all()
    )
