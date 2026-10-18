from celery.signals import worker_ready

from app.core.database import connect_to_mongo
from app.workers.async_loop import run_async


@worker_ready.connect
def init_worker_db(**_kwargs) -> None:
    run_async(connect_to_mongo())
