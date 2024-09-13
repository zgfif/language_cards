from core.models import Word
from rest_framework import permissions, viewsets
from django.db.models import Q
from core.api.serializers import WordSerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Word.objects.filter(added_by=self.request.user).order_by('know_native_to_studying', 'know_studying_to_native')

        word = self.request.query_params.get('word')
        translation = self.request.query_params.get('translation')
        common_query = self.request.query_params.get('q')

        if common_query:
            return queryset.filter(Q(translation__contains=common_query) | Q(word__contains=common_query))

        search_params = {}

        if translation:
            search_params['translation__contains'] = translation

        if word:
            search_params['word__contains'] = word

        if search_params:
            queryset = queryset.filter(**search_params)
        return queryset
