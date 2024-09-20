from core.models import Word
from rest_framework import serializers


class WordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    word = serializers.CharField()
    translation = serializers.CharField()
    sentence = serializers.CharField()
    full_audio_path = serializers.CharField()
    know_studying_to_native = serializers.BooleanField()
    know_native_to_studying = serializers.BooleanField()
    is_known = serializers.BooleanField()


class StudyingLanguageSerializer(serializers.Serializer):
    name = serializers.CharField()

