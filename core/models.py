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


class MyUser(User):
    class Meta:
        proxy = True

    def words(self):
        return Word.objects.filter(added_by=self.id)

    def known_words(self):
        return self.words().filter(en_ru=True, ru_en=True)

    def unknown_words(self):
        return self.words().filter(en_ru=False) | self.words().filter(ru_en=False)
