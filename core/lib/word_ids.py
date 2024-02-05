import random


class WordIds:
    def __init__(self, request=None, words=None):
        self.request = request
        self.words = words

    def update(self):
        ids = list(self.words.values_list('id', flat=True))
        en_ru_ids = list(self.words.filter(en_ru=False).values_list('id', flat=True))
        ru_en_ids = list(self.words.filter(ru_en=False).values_list('id', flat=True))
        random.shuffle(ids)
        random.shuffle(en_ru_ids)
        random.shuffle(ru_en_ids)
        self.request.session['word_ids'] = ids
        self.request.session['en_ru_ids'] = en_ru_ids
        self.request.session['ru_en_ids'] = ru_en_ids
        self.request.session.save()
