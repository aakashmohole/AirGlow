from fastapi import FastAPI
from app.api.dag import router as dag_router
from app.api.run import router as run_router
from app.db.database import Base, engine
from app.db.init_db import init_db
from app.models.output_file import OutputFile
from app.models.dag import DAG
from app.models.dag_runs import DAGRun
from app.models.dag_task import DAGTask
from app.api.dashboard import router as dashboard_router
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiting import limiter
from app.api.webhook import router as webhook_router
# Base.metadata.create_all(bind=engine) 


app= FastAPI(title="AirGlow")

app.state.limiter = limiter


app.add_middleware(
    SlowAPIMiddleware 
)

@app.on_event("startup")
def startup():
    init_db()


app.include_router(dag_router)
app.include_router(run_router)
app.include_router(dashboard_router)
app.include_router(webhook_router)