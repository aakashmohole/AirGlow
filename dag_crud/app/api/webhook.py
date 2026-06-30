from fastapi import APIRouter , Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"]
)


@router.post("",response_model=WebhookResponse)
def create_webhook(
    webhook:WebhookCreate,
    db:Session = Depends(get_db)
):
    new_webhook=  Webhook(
        dag_id= webhook.dag_id,
        callback_url=webhook.callback_url
    )
    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)

    return new_webhook


@router.get("",response_model=list[WebhookResponse])
def get_webhooks(db:Session=Depends(get_db)):
    return db.query(Webhook).all()


@router.delete("/{webhook_id}")
def delete_webhook(webhook_id:int,
                   db:Session=Depends(get_db)):
    
    webhook = (
        db.query(Webhook).filter(Webhook.id == webhook_id).first()
    )

    if not webhook: 
        raise HTTPException(
            status_code=404, detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()

    return{
        "message": "Webhook deleted successfully"
    }