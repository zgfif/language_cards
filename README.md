# language_cards

# Steps to deploy this project locally:

## first terminal:
1. Open the project's directory in **Terminal**l 
2. Run **python3 -m venv venv**
3. Run **source venv/bin/activate**
4. Run **pip install -r requirements.txt**
5. Run **python manage.py migrate**
6. Run **python manage.py runserver**

## second terminal:
1. Run **sudo service redis-server start**
2. Run **sudo service redis-server status** (it must have status ***active***)

## third terminal:
1. Open the project's directory in **Terminal**l 
2. Run **celery -A language_cards worker --pool=eventlet**
