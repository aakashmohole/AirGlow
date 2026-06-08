from app.db.database import Base
from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime


class DAG(Base):
    __tablename__="dags"

    id=Column(Integer, primary_key=True, index=True)
    dag_name=Column(String, nullable=False)
    dag_type=Column(String, nullable=False)  # etl/elt/batch
    scheduler=Column(String, nullable=False)    # auto/manual

    source_config=Column(JSON, nullable=False)
    transform_config=Column(JSON)
    destination_config=Column(JSON)

    created_at=Column(DateTime, default=datetime.utcnow)