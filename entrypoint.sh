#!/bin/sh

set -e

python scripts/create_database.py
alembic upgrade head
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
