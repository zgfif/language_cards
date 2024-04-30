from core.models import Word
from rest_framework import permissions, viewsets

from core.api.serializers import WordSerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Word.objects.filter(added_by=self.request.user).order_by('ru_en', 'en_ru')

        word = self.request.query_params.get('word')
        translation = self.request.query_params.get('translation')

        search_params = {}

        if translation:
            search_params['translation__contains'] = translation

        if word:
            search_params['word__contains'] = word

        if search_params:
            queryset = queryset.filter(**search_params)
        return queryset
