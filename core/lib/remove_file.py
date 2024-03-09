import os
from django.conf import settings


# this class was created to remove any file stored in media folder by its filename
class RemoveFile:
    MEDIA_ROOT = settings.MEDIA_ROOT

    def __init__(self,  filename=''):
        self.filename = filename

    def perform(self):
        path = self.absolute_path_to_file()
        if os.path.exists(path):
            os.remove(path)

    # returns absolute path to path through MEDIA_ROOT directory
    def absolute_path_to_file(self):
        if self.MEDIA_ROOT and self.filename:
            return os.path.join(self.MEDIA_ROOT, str(self.filename))
        else:
            return ''
