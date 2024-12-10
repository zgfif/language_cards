from celery import shared_task
from core.models import Word


@shared_task
def reset_word_progress(id):
    word = Word.objects.filter(id=id)
    if word[0]:
        print('reseting', word[0])
        word[0].reset_progress()

