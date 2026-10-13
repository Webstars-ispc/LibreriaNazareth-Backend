# Settings para correr la suite de tests localmente:
#   python manage.py test --settings=config.settings_test
from .settings import *  # noqa: F401,F403

SECRET_KEY = 'test-secret-key'
DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# El test client no negocia HTTPS: desactivamos el redirect para poder llamar a la API
SECURE_SSL_REDIRECT = False

# Hasher rápido para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
