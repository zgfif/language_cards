from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    sentence = models.CharField(max_length=255, blank=True)
    en_ru = models.BooleanField(default=False)
    ru_en = models.BooleanField(default=False)

    def __str__(self):
        return self.word

    def is_known(self):
        return self.ru_en and self.en_ru
