from celery import Celery

celery = Celery(
    "airglow_clone",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.worker.tasks"]
)

