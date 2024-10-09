import tempfile
import uuid
from django.core.files.base import ContentFile
from gtts import gTTS
from core.models import GttsAudio, Word


class GenerateAudio:
    TYPE_OF_FILE = 'mp3'  # by default, type is '.mp3'

    # the lang should be 'en' or 'bg'
    def __init__(self, word):
        self.word = word


    def perform(self):
        if not isinstance(self.word, Word):
            return None

        # if we have a studying word we will create an audition for this word.
        if self.word.word:
            self.bind_audition_to_word(text=self.word.word, use='word')
        
        # if we have a sentence we will create an audition for this sentence.
        if self.word.sentence:
            self.bind_audition_to_word(text=self.word.sentence, use='sentence')
    

    def bind_audition_to_word(self, text, use):
            # generate mp3 audition file for certain text
            tts = gTTS(text=text, lang=self.word.studying_lang.name)

            # Create a temporary file and save it as new record as GttsAudio model
            with tempfile.NamedTemporaryFile(suffix=f'.{self.TYPE_OF_FILE}', delete=False) as temp_audio_file:
                tts.save(temp_audio_file.name)

                # Read the content of the temporary file
                temp_audio_file.seek(0)  # Move the file pointer to the beginning
                audio_content = temp_audio_file.read()

                # save generated audio to media
                audio_content = ContentFile(audio_content, name=f'{self.generate_uuid()}.mp3')
                
                GttsAudio.objects.create(audio_name=audio_content, word=self.word, use=use)


    # each audio file should have unique name
    @staticmethod
    def generate_uuid():
        return uuid.uuid4()



