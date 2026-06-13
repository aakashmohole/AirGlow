from app.db.database import Base
from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime
from sqlalchemy.orm import relationship

class DAG(Base):
    __tablename__="dags"

    id=Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    dag_name=Column(String, nullable=False)
    dag_type=Column(String, nullable=False)  # etl/elt/batch
    scheduler_type=Column(String, default="manual")    # auto/manual
    cron_expression=Column(String, nullable=True)
    source_config=Column(JSON, nullable=False)
    transform_config=Column(JSON)
    destination_config=Column(JSON)

    created_at=Column(DateTime, default=datetime.utcnow)

    runs = relationship(
        "DAGRun",
        back_populates="dag",
        cascade="all , delete-orphan"
    )


print("DAG loaded")