from celery import shared_task
from datetime import datetime
from core.models import Word


@shared_task
def show_time():
    print(f'Time is: {datetime.now()}')


@shared_task
def reset_word_progress(id):
    word = Word.objects.get(id=id)
    print('reseting', word)
    word.reset_progress()

