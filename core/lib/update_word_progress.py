from core.lib.calculate_reset import CalculateReset
from core.tasks import reset_word_progress


class UpdateWordProgress:
    def __init__(self, word):
        self._word = word

    def perform(self):
        cr = CalculateReset(self._word.stage, self._word.times_in_row).perform()
        self._word.stage = cr.stage
        self._word.times_in_row = cr.times_in_row
        self._word.save()
        
        self.add_task(cr.reset_in_days)


    def add_task(self, days):
        # for test purposes we set 100 seconds for first run
        # reset_word_progress.apply_async((self._word.pk,), countdown=days * 24 * 60 * 60)
        reset_word_progress.apply_async((self._word.pk,), countdown=days * 400)

