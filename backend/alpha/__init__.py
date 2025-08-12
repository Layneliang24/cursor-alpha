from __future__ import annotations

import os

# Celery default app loader
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')

try:
    from .celery import app as celery_app  # type: ignore
    __all__ = ('celery_app',)
except Exception:
    # Celery is optional in dev
    pass

