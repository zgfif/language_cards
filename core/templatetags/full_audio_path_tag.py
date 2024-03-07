from django import template
from django.conf import settings

from core.lib.audio_file_path import AudioFilePath

register = template.Library()


# this template tag returns the path media file (if is locals), if not local returns the absolute path for file
# saved on GCS
@register.simple_tag
def full_path(word_obj):
    is_local = False if settings.SAVE_MEDIA_ON_GSC else True
    return AudioFilePath(word_obj).retrieve(is_local)

