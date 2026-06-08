from celery import Celery

celery = Celery(
    "dag_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)