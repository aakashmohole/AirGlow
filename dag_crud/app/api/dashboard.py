from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.dag import DAG
from app.models.dag_runs import DAGRun
from app.models.output_file import OutputFile

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def stats(db:Session=Depends(get_db)):
    return{
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
