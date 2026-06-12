from app.db.database import Base, engine
from app.models.dag import DAG
from app.models.dag_runs import DAGRun


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
    