from django.contrib.auth.models import User
from core.models import StudyingLanguage
from typing import Optional

"""
This class is used to calculate the user's progress in the language he is studying.
it calculates total progress, progress from native to studying language and progress from studying to native language.
"""

class CalculateUserProgress:
    TOTAL = 'total'
    STUDYING_TO_NATIVE = 'studying_to_native'
    NATIVE_TO_STUDYING = 'native_to_studying'

    filters = {
        TOTAL: {'know_native_to_studying': True, 'know_studying_to_native':True},
        STUDYING_TO_NATIVE: {'know_studying_to_native': True},
        NATIVE_TO_STUDYING: {'know_native_to_studying': True},
    }

    def __init__(self, user: User, studying_lang: StudyingLanguage) -> None:
        """
        Initialize the CalculateUserProgress instance.
        """
        self.words = user.word_set.filter(studying_lang=studying_lang)
        self.total_words_count = self.words.count()
    
    def perform(self, type_of_progress: str) -> Optional[float]:
        """
        Calculate the progress based on the type of progress.
        """
        if type_of_progress not in self.filters:
            raise ValueError('Invalid type of progress')
        
        if self.total_words_count == 0:
            return None
        
        known_count = self.words.filter(**self.filters[type_of_progress]).count() 
        
        return self.calculate_percentage(known_count)
        
    def calculate_percentage(self, known_count: int) -> float:
        """
        Calculate the percentage of known words.
        """
        if self.total_words_count == 0:
            return 0.0
        return round(known_count / (self.total_words_count / 100), 2)