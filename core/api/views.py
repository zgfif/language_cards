from core.models import Word, StudyingLanguage
from rest_framework import permissions, viewsets
from django.db.models import Q
from core.api.serializers import WordSerializer, StudyingLanguageSerializer 
from rest_framework.views import APIView
from rest_framework.response import Response 


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # which language the user is studying now
        studying_lang = self.request.user.profile.studying_lang

        # retrieve all user's words by studying_lang
        queryset = Word.objects.filter(studying_lang=studying_lang, added_by=self.request.user).order_by('know_native_to_studying', 'know_studying_to_native')

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


class ToggleLanguage(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, format=None):
        profile = request.user.profile
        
        target_studying_lang = request.data.get('studying_lang', None)
        
        if not target_studying_lang:
            return Response({'status': 'missing key studying_lang'})


        if target_studying_lang == 'None':
            profile.studying_lang = None
            
            profile.save()
            
            return Response({'status': 'ok', 'lang': 'None'})
        
        # retrieving StudyingLanguage object from existing studying languages
        studying_languages = StudyingLanguage.objects.filter(name=target_studying_lang)
            
        # assigning StudyingLanguage only if it already exists in db
        if not studying_languages:
            return Response({'status': 'invalid value of studying_lang'})
        
        profile.studying_lang = studying_languages[0]
        profile.save()
        
        return Response({'status': 'ok', 'lang': profile.studying_lang.name, 'full_lang_name': profile.studying_lang.full_name})

