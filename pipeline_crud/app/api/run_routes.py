from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.pipeline import Pipeline
from app.db.dependencies import get_db
from app.services.pipeline_runner import run_pipeline

router = APIRouter()

@router.get("/pipelines/{pipeline_id}/run")
def execute_pipeline(pipeline_id:int, db:Session=Depends(get_db)):
    pipeline=db.query(Pipeline).filter(pipeline.id==pipeline_id).first()
    if not pipeline:
        return{
            "Message" : "Pipeline Not Found"
        }
    df = run_pipeline(pipeline)
    return{
        "Message" : "Pipeline Executed.",
        "rows": len(df)
    }