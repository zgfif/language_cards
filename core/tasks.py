from celery import shared_task
from core.models import Word


@shared_task
def reset_word_progress(id):
    words = Word.objects.filter(id=id)
    if words.exists():
        print('reseting', words[0])
        words[0].reset_progress()

