from django import template

from core.lib.audio_file_path import AudioFilePath

register = template.Library()


# this template tag returns the path media file (if is locals), if not local returns the absolute path for file
# saved on GCS
@register.simple_tag
def full_audio_word_path(word):
    return word.full_audio_word_path 


@register.simple_tag
def full_audio_sentence_path(word):
    return word.full_audio_sentence_path 
