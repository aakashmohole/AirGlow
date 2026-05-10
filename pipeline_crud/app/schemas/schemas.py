from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any

class PipelineBase(BaseModel):
    name:str
    type:str
    source_type:str
    source_config:Optional[Dict]=None
    transform_config:Optional[Dict]=None
    destination_config:Optional[Dict]=None

class PipelineCreate(PipelineBase):
    pass

class PipelineUpdate(BaseModel):
    name:Optional[str]
    type:Optional[str]
    source_type:Optional[str]
    source_config:Optional[Dict]=None
    transform_config:Optional[Dict]=None
    destination_config:Optional[Dict]=None

class PipelineResponse(PipelineBase):
    id:int
    created_at:datetime

    class Config:
        from_attributes :True 