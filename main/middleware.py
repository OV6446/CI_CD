"""Дополнительные HTTP-заголовки безопасности для DAST и production."""


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=()'
        )
        response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        return response
