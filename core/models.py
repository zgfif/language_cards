import os.path

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.lib.remove_file import RemoveFile


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

    @property
    def audio_url(self):
        audios = GttsAudio.objects.filter(word=self)
        if audios:
            return audios.last().audio_name
        else:
            return None


class MyUser(User):
    class Meta:
        proxy = True

    def words(self):
        return Word.objects.filter(added_by=self.id)

    def known_words(self):
        return self.words().filter(en_ru=True, ru_en=True)

    def unknown_words(self):
        return self.words().filter(en_ru=False) | self.words().filter(ru_en=False)


class GttsAudio(models.Model):
    audio_name = models.FileField(upload_to='my_files/', blank=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.audio_name)


@receiver(post_delete, sender=GttsAudio)
def signal_remove_audio_file(sender, instance, using, **kwargs):
    RemoveFile(instance.audio_name).perform()

