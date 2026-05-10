from fastapi import FastAPI
from app.api.pipeline_routes import router as pipeline_router
from app.db.database import engine, Base
from app.models.pipeline import Pipeline

app=FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(pipeline_router)