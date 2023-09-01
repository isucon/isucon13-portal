#!/bin/bash -xe

export PYTHONUNBUFFERED=TRUE

TASK=$1

function start_api () {
    sleep "$((RANDOM % 20))"
    python manage.py migrate
    /usr/sbin/nginx -g "daemon off;" &
    gunicorn --bind 0.0.0.0:8000 -w 3 --max-requests 3000 --max-requests-jitter 500 isucon.portal.wsgi:application --capture-output --error-logfile -
}

case "${TASK}" in
  "api" ) start_api ;;
esac
