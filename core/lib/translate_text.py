from googletrans import Translator
from httpcore._exceptions import ConnectError


class TranslateText:
    # source_lang ("ru", "en", "es", "fr", "de", "ja")
    # target_lang ("ru", "en", "es", "fr", "de", "ja")
    def __init__(self, source_lang, target_lang):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = Translator()

    def perform(self, text=''):
        if text and isinstance(text, str):
            try:
                return self.translator.translate(text, src=self.source_lang, dest=self.target_lang).text
            except ConnectError as e:
                return ''
