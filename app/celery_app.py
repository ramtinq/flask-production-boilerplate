import os
from celery import Celery, Task
from .utils import read_secret

_broker_url = (
    f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}"
    f"@{os.getenv('RABBITMQ_HOST', 'rabbitmq')}:{os.getenv('RABBITMQ_PORT', '5672')}/"
)

celery = Celery(
    "app",
    broker=_broker_url,
    backend=os.getenv("CELERY_BACKEND_URL"),
    broker_connection_retry_on_startup=True,
    broker_transport_options = {"max_retries": 10},
    include=[
        "app.blueprints.core.tasks",
        "app.blueprints.auth.tasks",
        "app.blueprints.calculations.tasks"
    ]
)