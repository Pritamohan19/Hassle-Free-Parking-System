LOGIN_REDIRECT_URL = 'parking:dashboard'  # Use the correct namespace and URL name

CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

MIDDLEWARE = [
    # ...existing middleware...
    'django.middleware.csrf.CsrfViewMiddleware',  # Ensure this is included
    # ...existing middleware...
]

INSTALLED_APPS = [
    # ...existing apps...
    'parking',  # Ensure this is included
    # ...existing apps...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default authentication backend
]
