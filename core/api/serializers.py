from core.models import Word
from rest_framework import serializers


class WordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    word = serializers.CharField()
    translation = serializers.CharField()
    sentence = serializers.CharField()
    full_audio_path = serializers.CharField()
    en_ru = serializers.BooleanField()
    ru_en = serializers.BooleanField()
    is_known = serializers.BooleanField()
