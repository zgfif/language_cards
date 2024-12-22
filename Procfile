web: python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --no-input && python manage.py auto_create_superuser && gunicorn language_cards.wsgi
worker: celery -A language_cards worker --pool=eventlet

