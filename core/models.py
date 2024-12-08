import os.path

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from core.lib.audio_file_path import AudioFilePath
from core.lib.remove_file import RemoveFile
from core.lib.remove_from_gcs import RemoveFromGcs
from language_cards import settings

# these languages will be used in as possible target languages
STUDYING_LANGUAGES = [
    ('en', 'English'),
    ('bg', 'Bulgarian'),
]


#  validate if the value is empty
def empty_validator(value: str):
    if value == '':
        raise ValidationError("This field cannot be an empty string.")


class StudyingLanguage(models.Model):
    name = models.CharField(choices=STUDYING_LANGUAGES,
                            max_length=255, unique=True,
                            blank=False,
                            null=False,
                            validators=[empty_validator])

    def __str__(self):
        return self.name
    
    @property
    def full_name(self):
        return self.get_name_display()


class Word(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    sentence = models.CharField(max_length=255, blank=True)
    know_native_to_studying = models.BooleanField(default=False)
    know_studying_to_native = models.BooleanField(default=False)
    studying_lang = models.ForeignKey(StudyingLanguage, on_delete=models.CASCADE)
    stage = models.CharField(max_length=100, default='day')
    times_in_row = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word

    def reset_progress(self):
        self.know_native_to_studying, self.know_studying_to_native = False, False
        self.save()

    @property
    def is_known(self):
        return self.know_native_to_studying and self.know_studying_to_native

    @property
    def audio_word_name(self):
        audios = GttsAudio.objects.filter(word=self, use='word')
        if audios:
            return audios.last().audio_name
        else:
            return None

    @property
    def audio_sentence_name(self):
        audios = GttsAudio.objects.filter(word=self, use='sentence')
        
        if audios:
            return audios.last().audio_name
        else:
            return None

    @property
    def full_audio_word_path(self):
        is_local = False if settings.SAVE_MEDIA_ON_GSC else True
        gtts = GttsAudio.objects.filter(word=self, use='word').last()
        if gtts:
            return AudioFilePath(gtts.audio_name).retrieve(is_local)
    
    @property
    def full_audio_sentence_path(self):
        is_local = False if settings.SAVE_MEDIA_ON_GSC else True
        gtts = GttsAudio.objects.filter(word=self, use='sentence').last()
        if gtts:
            return AudioFilePath(gtts.audio_name).retrieve(is_local)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    studying_lang = models.ForeignKey(StudyingLanguage, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f'{self.user} studying: {self.studying_lang}'

    @property
    def available_languages(self):
        if self.studying_lang:
            return StudyingLanguage.objects.exclude(name=self.studying_lang.name) 
        else: 
            return StudyingLanguage.objects.all()



class MyUser(User):
    class Meta:
        proxy = True
    
    @property
    def words(self):
        return Word.objects.filter(added_by=self.id, studying_lang=self.profile.studying_lang)
    
    @property
    def known_words(self):
        return self.words.filter(know_studying_to_native=True, know_native_to_studying=True)

    @property
    def unknown_words(self):
        return self.words.filter(know_studying_to_native=False) | self.words.filter(know_native_to_studying=False)


class GttsAudio(models.Model):
    USE_CHOICES = [('word', 'for_word'), ('sentence', 'for_sentence')]

    audio_name = models.FileField(upload_to='my_files/', blank=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    use = models.CharField(max_length=255, choices=USE_CHOICES)

    def __str__(self):
        return str(f'{self.audio_name}')


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


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance=None, created=False, **kwargs):
    # as soon as we create a new user we also create a new profile for him
    if created:
        Profile.objects.create(user=instance)


