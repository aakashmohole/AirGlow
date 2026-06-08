from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.dag import DAG
from app.schemas.dag import DAGCreate, DAGResponse
from app.db.dependencies import get_db



router=APIRouter(prefix="/dags",tags=["DAGs"])


@router.post("/", response_model=DAGResponse)
def create_dag(payload: DAGCreate, db: Session = Depends(get_db)):
    
    dag=DAG(
        dag_name=payload.dag_name,
        dag_type=payload.dag_type,
        scheduler=payload.scheduler,
        source_config=payload.source_config,
        transform_config=payload.transform_config,
        destination_config=payload.destination_config
    )


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
def update_dag(dag_id:int, payload:DAGCreate, db:Session=Depends(get_db)):
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
    
    db.delete(dag)
    db.commit()
    return {"Message":"DAG Deleted Successfully"}