import random


class WordIds:
    def __init__(self, request=None, words=None):
        self.request = request
        self.words = words

    def update(self):
        ids = list(self.words.values_list('id', flat=True))
        studying_to_native_ids = list(self.words.filter(know_studying_to_native=False).values_list('id', flat=True))
        native_to_studying_ids = list(self.words.filter(know_native_to_studying=False).values_list('id', flat=True))
        random.shuffle(ids)
        random.shuffle(studying_to_native_ids)
        random.shuffle(native_to_studying_ids)

        self.request.session['word_ids'] = ids
        self.request.session['native_to_studying_ids'] = native_to_studying_ids
        self.request.session['studying_to_native_ids'] = studying_to_native_ids

        self.request.session.save()
