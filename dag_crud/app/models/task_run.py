from app.db.database import Base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey ,DateTime
from datetime import  datetime

class TaskRun(Base):
    __tablename__ = 'task_runs'

    id = Column(Integer, primary_key=True, index=True)
    dag_run_id = Column(Integer, ForeignKey('dag_runs.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('dag_tasks.id'), nullable=False)
    status = Column(String(50), nullable=False , default='queued')
    logs = Column(JSON, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)