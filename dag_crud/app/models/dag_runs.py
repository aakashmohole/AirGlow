from sqlalchemy import JSON, Column, ForeignKey, Integer, String ,DateTime
from app.db.database import Base
from datetime import datetime   
from sqlalchemy.orm import relationship

class DAGRun(Base):
    __tablename__ = "dag_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(Integer, ForeignKey("dags.id", ondelete="CASCADE"))
    status = Column(String, default="queued")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    log = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    dag = relationship(
        "DAG",
        back_populates="runs"
    )