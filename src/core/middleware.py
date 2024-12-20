from django.utils.translation import activate
from .utils import get_language_from_request
from django.http import Http404

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Activate the language for this request
        language = get_language_from_request(request)
        activate(language)
        
        response = self.get_response(request)
        
        # Add language to response headers
        response['Content-Language'] = language
        return response

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.META.get('REMOTE_ADDR') not in ['127.0.0.1', 'localhost']:
                raise Http404()
        return self.get_response(request)