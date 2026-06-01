from fastapi import FastAPI
from app.api.pipeline_routes import router as pipeline_router
from app.db.database import engine, Base
from app.models.pipeline import Pipeline
from app.api.run_routes import router as run_router
from app.api.steps_routes import router as steps_router

app=FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(pipeline_router)



app.include_router(steps_router)
app.include_router(run_router)