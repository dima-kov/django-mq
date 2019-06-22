from django.conf import settings


SEE = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
