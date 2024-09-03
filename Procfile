web: newrelic-admin run-program gunicorn my_api.wsgi -w 4 --log-file -
rqworker: python manage.py rqworker default
rqscheduler: python manage.py rqscheduler default --interval $RQ_SCHEDULER_INTERVAL