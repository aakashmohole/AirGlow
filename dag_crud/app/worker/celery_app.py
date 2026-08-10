from celery import Celery

celery = Celery(
    "airglow_clone",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.worker.tasks"]
)

celery.conf.beat_schedule = {
    "scan-dags-every-minute":{
        "task": "app.worker.tasks.scan_and_trigger_dags",
        "schedule": 60.0
    }
    }
