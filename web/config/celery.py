import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("iomat")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Celery OK: request={self.request!r}")
