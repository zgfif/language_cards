class WordIds:
    def __init__(self, request=None, words=None):
        self.request = request
        self.words = words

    def update(self):
        ids = list(self.words.values_list('id', flat=True))
        self.request.session['word_ids'] = ids
