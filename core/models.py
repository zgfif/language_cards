import os.path

from django.db import models
from django.contrib.auth.models import User


from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from core.lib.audio_file_path import AudioFilePath
from core.lib.remove_file import RemoveFile
from core.lib.remove_from_gcs import RemoveFromGcs
from language_cards import settings


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
    def audio_name(self):
        audios = GttsAudio.objects.filter(word=self)
        if audios:
            return audios.last().audio_name
        else:
            return None

    @property
    def full_audio_path(self):
        is_local = False if settings.SAVE_MEDIA_ON_GSC else True
        return AudioFilePath(self).retrieve(is_local)


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
    # remove local file saved in MEDIA_ROOT directory
    RemoveFile(instance.audio_name).perform()
    # remove audio file if it was saved in Google Cloud Storage
    # RemoveFromGcs(credentials=settings.GS_CREDENTIALS, bucket_name=settings.GS_BUCKET_NAME).perform(instance.audio_name)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    # as soon as we create a new user we also create an auth token for him and save it to db
    if created:
        Token.objects.create(user=instance)
