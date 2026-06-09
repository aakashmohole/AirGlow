from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON

class DAGTask(Base):
    __tablename__ = "dag_tasks"

    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(Integer, ForeignKey("dags.id"))

    task_name = Column(String, nullable=False)
    task_type = Column(String, nullable=False)

    order_index = Column(Integer, nullable=False)

    config = Column(JSON)