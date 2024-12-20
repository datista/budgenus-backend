from django.utils.translation import activate
from django.conf import settings

def get_language_from_request(request):
    """Get language from request header or default to settings"""
    default_language = settings.LANGUAGE_CODE
    language = request.headers.get('Accept-Language', default_language)
    # Return first two characters (language code) and ensure it's supported
    lang_code = language[:2].lower()
    if lang_code in dict(settings.LANGUAGES):
        return lang_code
    return default_language