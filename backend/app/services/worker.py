"""Celery app + async tasks with retry."""
from celery import Celery

from app.config.settings import get_settings

settings = get_settings()
celery_app = Celery("finai", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", result_serializer="json",
                       accept_content=["json"], task_acks_late=True)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_document_task(self, document_id: str):
    from app.services.document_service import process_document
    try:
        process_document(document_id)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_analysis_task(self, run_id: str):
    from app.services.analysis_service import execute_analysis_run
    try:
        execute_analysis_run(run_id)
    except Exception as exc:
        raise self.retry(exc=exc)
