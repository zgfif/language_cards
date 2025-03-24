class CalculateUserProgress:
    def __init__(self, user, studying_lang):
        self.words = user.word_set.filter(studying_lang=studying_lang)

    def total(self):
        if self.words.count() == 0:
            return None
        total_count = self.words.count()
        known_count = self.words.filter(know_native_to_studying=True, know_studying_to_native=True).count()
        return round(known_count / (total_count / 100), 2)
        
  
    def studying_to_native(self):
        if self.words.count() == 0:
            return None
        total_count = self.words.count()
        known_count = self.words.filter(know_studying_to_native=True).count()
        return round(known_count / (total_count / 100), 2)
    
    def native_to_studying(self):
        if self.words.count() == 0:
            return None
        total_count = self.words.count()
        known_count = self.words.filter(know_native_to_studying=True).count()
        return round(known_count / (total_count / 100), 2)