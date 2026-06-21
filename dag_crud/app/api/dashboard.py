from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.dag import DAG
from app.models.dag_runs import DAGRun
from app.models.output_file import OutputFile
from app.core.cache import redis_client
import json

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def stats(db:Session=Depends(get_db)):

    cache = redis_client.get("dashboard_stats")
    if cache:
        return json.loads(cache)

    result = {
        "total_dags":
            db.query(DAG).count(),

        "total_runs":
            db.query(DAGRun).count(),

        "successful_runs":
            db.query(DAGRun)
            .filter(DAGRun.status == "success").count(),

        "failed_runs":
            db.query(DAGRun)
            .filter(DAGRun.status == "failed")
            .count(),

        "files_generated":
            db.query(OutputFile).count()
    }

    redis_client.setex(
        "dashboard_stats",
        60,
        json.dumps(result)
    )
    return result
