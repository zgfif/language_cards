from core.models import Word
from rest_framework import permissions, viewsets

from core.api.serializers import WordSerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all().order_by('en_ru', 'ru_en')
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]
