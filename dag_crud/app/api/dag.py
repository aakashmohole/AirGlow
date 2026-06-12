from fastapi import APIRouter, HTTPException, Depends
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


router=APIRouter(prefix="/dags",tags=["DAGs"])


@router.post("/", response_model=DAGResponse)
def create_dag(payload: DAGCreate, db: Session = Depends(get_db)):
    
    dag=DAG(**payload.dict())
    db.add(dag)
    db.commit()
    db.refresh(dag)
    return dag

@router.get("/", response_model=list[DAGResponse])
def get_dags(db: Session = Depends(get_db)):
    dags = db.query(DAG).all()
    return dags



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
    dag.scheduler=payload.scheduler
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
    db: Session = Depends(get_db)
):
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

    if file.file_type == "json":
        return Response(
            content=json.dumps(file.content, indent=4),
            media_type="application/json",
            headers={
                "Content-Disposition":
                f'attachment; filename="{file.file_name}"'
            }
        )

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