from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any, List,Union

class APISource(BaseModel):
    type:str="api"
    url: str
    method: str ="GET"
    headers: Optional[dict]={}

class CSVSource(BaseModel):
    type:str="csv"
    file_path:str

class DBSource(BaseModel):
    type:str="db"
    host:str
    database:str
    query:str

class TransformRule(BaseModel):
    type:str
    column:Optional[str]=None
    value:Optional[Any]=None

class DestionationConfig(BaseModel):
    type:str
    table:str

Source_config=Union[APISource, CSVSource, DBSource]



class DAGCreate(BaseModel):
    dag_name:str
    dag_type:str
    scheduler:str
    source_config:Source_config
    transform_config:list[TransformRule]=None
    destination_config:DestionationConfig


class DAGResponse(BaseModel):
    id:int
    dag_name:str
    dag_type:str
    scheduler:str
    source_config:Source_config
    transform_config:List[TransformRule]=None
    destination_config:DestionationConfig   
    created_at:datetime










    class Config:
        from_attributes = True
