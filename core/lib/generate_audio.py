import tempfile
import uuid
from django.core.files.base import ContentFile
from gtts import gTTS
from core.models import GttsAudio

class GenerateAudio:
    TYPE_OF_FILE = 'mp3'  # by default, type is '.mp3'

    # should be 'en' or 'bg'
    def __init__(self, word, lang='en'):
        self.word = word
        self.lang = lang


    def perform(self):
        if self.word:
            # generates mp3 file which contains the text
            tts = gTTS(text=self.word.word, lang=self.word.studying_lang.name)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{self.TYPE_OF_FILE}', delete=False) as temp_audio_file:
                tts.save(temp_audio_file.name)

                # Read the content of the temporary file
                temp_audio_file.seek(0)  # Move the file pointer to the beginning
                audio_content = temp_audio_file.read()

                # save generated audio to media
                # self.save_audio(audio_content)
                audio_content = ContentFile(audio_content, name=f'{self.generate_uuid()}.mp3')
                
                GttsAudio.objects.create(audio_name=audio_content, word=self.word, use='word')

                if self.word.sentence:
                    # generates mp3 file which contains the text
                    tts = gTTS(text=self.word.sentence, lang=self.word.studying_lang.name)

                    # Create a temporary file
                    with tempfile.NamedTemporaryFile(suffix=f'.{self.TYPE_OF_FILE}', delete=False) as temp_audio_file:
                        tts.save(temp_audio_file.name)

                        # Read the content of the temporary file
                        temp_audio_file.seek(0)  # Move the file pointer to the beginning
                        audio_content = temp_audio_file.read()

                        # save generated audio to media
                        # self.save_audio(audio_content)
                        audio_content = ContentFile(audio_content, name=f'{self.generate_uuid()}.mp3')
                
                        GttsAudio.objects.create(audio_name=audio_content, word=self.word, use='sentence')


    # each audio file should have unique name
    @staticmethod
    def generate_uuid():
        return uuid.uuid4()

