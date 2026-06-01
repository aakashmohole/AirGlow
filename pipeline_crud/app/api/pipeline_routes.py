from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.pipeline import Pipeline
from app.schemas.schemas import PipelineCreate, PipelineUpdate, PipelineResponse
from app.db.dependencies import get_db



router=APIRouter(prefix="/pipelines",tags=["Pipelines"])




@router.post("/", response_model=PipelineResponse)
def create_pipeline(pipeline:PipelineCreate, db:Session=Depends(get_db)):
    new_pipeline=Pipeline(**pipeline.model_dump())
    db.add(new_pipeline)
    db.commit()
    db.refresh(new_pipeline)
    return new_pipeline


@router.get("/", response_model=list[PipelineResponse])
def get_pipelines(db: Session = Depends(get_db)):
    pipelines = db.query(Pipeline).all()
    return pipelines

@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id:int, db:Session=Depends(get_db)):
    pipeline=db.query(Pipeline).filter(Pipeline.id==pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline Not Found")
    
    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(pipeline_id:int, data:PipelineUpdate, db:Session=Depends(get_db)):
    pipeline=db.query(Pipeline).filter(Pipeline.id==pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline Not Found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(pipeline, key, value)

    db.commit()
    db.refresh(pipeline)
    return pipeline



@router.delete("/{pipeline_id}")
def delete_pipeline(pipeline_id:int, db:Session=Depends(get_db)):
    pipeline=db.query(Pipeline).filter(Pipeline.id==pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline Not Found")
    
    db.delete(pipeline)
    db.commit()
    return {"Message":"Pipeline Deleted"}