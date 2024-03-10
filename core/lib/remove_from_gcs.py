from google.cloud import storage
from django.conf import settings
from google.api_core.exceptions import NotFound


# before using this class ensure that GS_CREDENTIALS and GS_BUCKET_NAME were set in your settings.py
# this class is used to delete files from Google Cloud Storage. Any file could be removed by its name OR/AND its name
# and containing directory
class RemoveFromGcs:
    CREDENTIALS = settings.GS_CREDENTIALS
    BUCKET_NAME = settings.GS_BUCKET_NAME

    def __init__(self):
        storage_client = storage.Client(credentials=self.CREDENTIALS)
        self.bucket = storage_client.bucket(self.BUCKET_NAME)

    # for testing, I used "my_files/fe880aea-479c-4f36-b8a9-808fe4337188.mp3" format
    # where my_files is the directory which contains .mp3 file in the bucket
    def perform(self, blob_name=''):
        if blob_name:
            blob = self.bucket.blob(str(blob_name))
            try:
                blob.delete()
            except NotFound as e:
                print('blob is not found:', e)

