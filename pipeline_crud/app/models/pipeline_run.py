from sqlalchemy import Column, DateTime,ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class PipelineRun(Base):
    __tablename__="pipeline_runs"
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"))
    status = Column(String, default="pending")
    start_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    logs = Column(String, nullable=True)