from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON

class Webhook(Base):
    __tablename__ ="webhooks"

    id = Column(Integer, primary_key=True, index=True)
    dag_id=Column(Integer, ForeignKey("dags.id"), ondelete="CASECADE")
    callback_url=Column(String)