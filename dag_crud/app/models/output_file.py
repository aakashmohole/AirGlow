from sqlalchemy import Column , Integer, String, ForeignKey, Text , JSON
from app.db.database import Base


class OutputFile(Base):
    __tablename__="output_files"
                                                                                                      
    id= Column(Integer, primary_key=True, index=False)
    run_id = Column(
        Integer,
        ForeignKey("dag_runs.id")
    )
    dag_id = Column(Integer, ForeignKey("dags.id"))

    file_name=Column(String)                                                  
    file_type=Column(String)
    records_count=Column(Integer)

    content = Column(JSON)


print("OutputFile loaded")