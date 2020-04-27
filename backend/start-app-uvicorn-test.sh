#!/bin/sh
export DJANGO_SETTINGS_MODULE="backend.settings"
uvicorn backend.asgi:application
