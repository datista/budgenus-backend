from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.utils.translation import activate, gettext as _

class LanguageView(APIView):
    def get(self, request):
        """Get available languages and current language"""
        current_language = request.LANGUAGE_CODE
        available_languages = dict(settings.LANGUAGES)
        
        return Response({
            'current': current_language,
            'available': available_languages
        })

    def post(self, request):
        """Change language"""
        language = request.data.get('language')
        
        if language not in dict(settings.LANGUAGES):
            return Response({
                'error': _('Invalid language code')
            }, status=400)
            
        activate(language)
        return Response({
            'current': language,
            'message': _('Language changed successfully')
        })
