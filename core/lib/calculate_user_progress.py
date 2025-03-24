from django.contrib.auth.models import User
from core.models import StudyingLanguage
from typing import Optional

"""
This class is used to calculate the user's progress in the language he is studying.
it calculates total progress, progress from native to studying language and progress from studying to native language.
"""

class CalculateUserProgress:
    filters = {
        'total': {'know_native_to_studying': True, 'know_studying_to_native':True},
        'studying_to_native': {'know_studying_to_native': True},
        'native_to_studying': {'know_native_to_studying': True},
    }

    def __init__(self, user: User, studying_lang: StudyingLanguage) -> None:
        self.words = user.word_set.filter(studying_lang=studying_lang)
    
    def perform(self, type_of_progress: str) -> Optional[float]:
        if type_of_progress not in ['total', 'studying_to_native', 'native_to_studying']:
            raise ValueError('Invalid type of progress')
        
        if self.words.count() == 0:
            return None
        
        known_count = self.words.filter(**self.filters[type_of_progress]).count() 
        
        return self.calculate_percentage(known_count)
        
    def calculate_percentage(self, known_count: int) -> float:
        if self.words.count() == 0:
            return 0.0
        return round(known_count / (self.words.count() / 100), 2)