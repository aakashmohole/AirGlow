from fastapi import APIRouter
from app.config.pipeline_steps import PIPELINE_STEPS

router = APIRouter()

@router.get("/pipeline_steps/{pipeline_type}")
def get_pipeline_steps(pipeline_type:str):
    return PIPELINE_STEPS.get(pipeline_type,[])