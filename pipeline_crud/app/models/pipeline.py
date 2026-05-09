from app.db.database import Base
from sqlalchemy  import Colunm , String, Intger
from datetime import datetime

class Pipeline(BaseModel):
    __tablename__="pipelines"

    id=