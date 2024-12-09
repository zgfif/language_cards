from celery import shared_task
from core.models import Word


@shared_task
def reset_word_progress(id):
    word = Word.objects.get(id=id)
    print('reseting', word)
    word.reset_progress()

