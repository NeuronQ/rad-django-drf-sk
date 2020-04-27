#!/bin/sh
export BIND="unix:/tmp/backend-admin-gunicorn.sock"
/path/to/gunicorn \
  -k uvicorn.workers.UvicornWorker \
  -c /path/to/your/backend/gunicorn_conf.py \
  backend.asgi:application
