release: python manage.py migrate
web: gunicorn config.wsgi:application
worker: REMAP_SIGTERM=SIGQUIT celery -A Ecommerce.tasks worker -l info --without-gossip --without-mingle --without-heartbeat
beat: REMAP_SIGTERM=SIGQUIT celery -A Ecommerce.tasks beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
