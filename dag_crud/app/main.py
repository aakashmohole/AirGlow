from fastapi import FastAPI
from app.api.dag import router as dag_router
from app.api.run import router as run_router
from app.db.database import Base, engine
from app.db.init_db import init_db


app= FastAPI(title="AirGlow")


@app.on_event("startup")
def startup():
    init_db()


app.include_router(dag_router)
app.include_router(run_router)