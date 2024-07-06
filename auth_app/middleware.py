from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse({
                "errors": exception.message_dict['errors'] if 'errors' in exception.message_dict else exception.message_dict
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return None