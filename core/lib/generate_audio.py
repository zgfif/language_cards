import tempfile

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from gtts import gTTS
from core.models import GttsAudio


class GenerateAudio(BaseCommand):
    def perform(self, word, *args, **options):
        # generates mp3 file which contains spelled text
        tts = gTTS(text=word.word, lang='en')

        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
            tts.save(temp_audio_file.name)

            # Read the content of the temporary file
            temp_audio_file.seek(0)  # Move the file pointer to the beginning
            audio_content = temp_audio_file.read()

        content_file = ContentFile(audio_content, name=f'{word.word}.mp3')
        ga = GttsAudio(word=word, audio_name=content_file)

        ga.save()
