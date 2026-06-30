from pydantic import BaseModel, HttpUrl

class WebhookCreate(BaseModel):
    dag_id:int
    callback_url:HttpUrl

class WebhookResponse(BaseModel):
    id:int
    dag_id:int
    callback_url:HttpUrl

    class config:
        form_attributes=True