from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text ,DateTime
from app.db.database import Base
from datetime import datetime   

class DAGRun(Base):
    __tablename__ = "dag_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(Integer, ForeignKey("dags.id"))
    status = Column(String(50), default="queued")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    log = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)