class AudioFilePath:
    def __init__(self, obj):
        self.relative_path = obj.audio_name

    def retrieve(self, is_local=True):
        prefix = self.local_file_prefix() if is_local else self.google_bucket_prefix()
        return prefix + str(self.relative_path)

    @staticmethod
    def google_bucket_prefix():
        return 'https://storage.googleapis.com/upload_photos_bucket/'

    @staticmethod
    def local_file_prefix():
        return '/media/'
