class AudioFilePath:
    def __init__(self, audio_name):
        self.audio_name = audio_name

    def retrieve(self, is_local=True):
        if not self.audio_name:
            return None

        prefix = self.local_file_prefix() if is_local else self.google_bucket_prefix()
        return prefix + str(self.audio_name)

    @staticmethod
    def google_bucket_prefix():
        return 'https://storage.googleapis.com/upload_photos_bucket/'

    @staticmethod
    def local_file_prefix():
        return '/media/'
