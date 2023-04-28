#!/bin/bash

if [ "$APP_MODE" == "worker" ]; then
  # Start the Celery worker
  celery -A app.tasks:celery worker -n ${MODS_WORKER_NAME} --loglevel debug
elif [ "$APP_MODE" == "server" ]; then
  # Start the Hypercorn server
  hypercorn app.main:app --bind 0.0.0.0:8080
else
  # Invalid APP_MODE value
  echo "Invalid APP_MODE value: $APP_MODE"
fi
