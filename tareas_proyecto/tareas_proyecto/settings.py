"""
Django settings for tareas_proyecto project.
"""

from pathlib import Path
import os
from decouple import config, Csv  # 👈 para leer variables del .env
from decimal import getcontext, InvalidOperation, DivisionByZero, Overflow

# ==============================
#   BASE DIR
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
#   VARIABLES DE ENTORNO
# ==============================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv()
)

# ==============================
#       APLICACIONES
# ==============================
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps
    'tareas',
    'tareasMauri',
    'usuarios',
    "finanzas.apps.FinanzasConfig",

    # Login con Google
    'social_django',
]

# ==============================
#       MIDDLEWARE
# ==============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Social Auth
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'tareas_proyecto.urls'

# ==============================
#       TEMPLATES
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Social auth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'tareas_proyecto.wsgi.application'

# ==============================
#       BASE DE DATOS (BLINDADA)
# ==============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',

        # Opciones seguras
        'OPTIONS': {
            'timeout': 20,
            'detect_types': 1,
        },
    }
}

# ==============================
#   BLINDAJE GLOBAL DECIMAL
# ==============================
ctx = getcontext()
ctx.traps[InvalidOperation] = True
ctx.traps[DivisionByZero] = True
ctx.traps[Overflow] = True

# ==============================
#   VALIDACIÓN DE CONTRASEÑAS
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================
#   INTERNACIONALIZACIÓN
# ==============================
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]

# ==============================
#   ARCHIVOS ESTÁTICOS
# ==============================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# ==============================
#   LOGIN / LOGOUT
# ==============================
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'tareas:dashboard'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# ==============================
#   SOCIAL AUTH (GOOGLE)
# ==============================
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account',
}

SOCIAL_AUTH_GOOGLE_OAUTH2_REVOKE_TOKENS_ON_DISCONNECT = True

# ==============================
#   CLAVE AUTOMÁTICA
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'