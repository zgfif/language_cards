import tempfile
import uuid
from django.core.files.base import ContentFile
from gtts import gTTS
from core.models import GttsAudio, Word


class GenerateAudio:
    LANG = 'en'  # by default, convert text to English
    TYPE_OF_FILE = 'mp3'  # by default, type is '.mp3'

    def __init__(self, word):
        if isinstance(word, Word):
            self.word = word
            if isinstance(word.word, str) and len(word.word) > 0:
                self.text = word.word
        else:
            raise AttributeError('argument must be instance of Word')

    def perform(self):
        if self.text:
            # generates mp3 file which contains the text
            tts = gTTS(text=self.text, lang=self.LANG)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{self.TYPE_OF_FILE}', delete=False) as temp_audio_file:
                tts.save(temp_audio_file.name)

                # Read the content of the temporary file
                temp_audio_file.seek(0)  # Move the file pointer to the beginning
                audio_content = temp_audio_file.read()

                # save generated audio to media
                self.save_audio(audio_content)
        else:
            return None

    def save_audio(self, audio_content=None):
        if audio_content:
            content_file = ContentFile(audio_content, name=f'{self.generate_uuid()}.mp3')
            # initialize GttsAudio model with file and reference to word
            ga = GttsAudio(word=self.word, audio_name=content_file)
            ga.save()

    # each audio file should have unique name
    @staticmethod
    def generate_uuid():
        return uuid.uuid4()
