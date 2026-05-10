from app.db.database import Base
from sqlalchemy  import Column , String, Integer, DateTime, JSON
from datetime import datetime


class Pipeline(Base):
    __tablename__="pipelines"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    type=Column(String, nullable=False)
    source_type=Column(String, nullable=False)

    source_config=Column(JSON)
    transform_config=Column(JSON)
    destination_config=Column(JSON)

    created_at=Column(DateTime, default=datetime.utcnow)