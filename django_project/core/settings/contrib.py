"""Settings for 3rd party."""
import ast

from .base import *  # noqa

# Extra installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework_gis',
    'webpack_loader',
    'guardian',
    'django_cleanup.apps.CleanupConfig',
    'easyaudit',
    'django_celery_beat',
    'django_celery_results',
    # Configure the django-otp package.
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    # Enable two-factor auth.
    'allauth_2fa',
    'docs_crawler',
)
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'frontend/',  # must end with slash
        'STATS_FILE': absolute_path('frontend', 'webpack-stats.prod.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_VERSIONING_CLASS': (
        'rest_framework.versioning.NamespaceVersioning'
    ),
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'guardian.backends.ObjectPermissionBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
CELERY_RESULT_BACKEND = 'django-db'

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'django.template.context_processors.request',
]

MAPTILER_API_KEY = os.environ.get('MAPTILER_API_KEY', '')

# ACCOUNT config
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_FORMS = {
    'signup': 'sawps.forms.CustomSignupForm',
    'login': 'sawps.forms.CustomLoginForm',
    'change_password': 'sawps.forms.CustomChangePasswordForm',
}
ACCOUNT_AUTHENTICATION_METHOD = 'email'

AUTH_WITH_EMAIL_ONLY = True

# Password validator
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "sawps.password_validation.NumberValidator",
    },
    {
        "NAME": "sawps.password_validation.UppercaseValidator",
    },
    {
        "NAME": "sawps.password_validation.SymbolValidator",
    },
]

CONTACT_US_RECIPIENTS = ast.literal_eval(os.environ.get('CONTACT_US_RECIPIENTS', "['amy@kartoza.com']"))
SUPPORT_EMAIL = 'amy@kartoza.com'

MIDDLEWARE += (
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
)

DISABLE_2FA = ast.literal_eval(os.environ.get('DISABLE_2FA', 'False'))
if DISABLE_2FA:
    MIDDLEWARE = [m for m in MIDDLEWARE if m != 'sawps.middleware.RequireSuperuser2FAMiddleware']

DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = [
    'django_celery_beat.PeriodicTask',
    'django_celery_beat.PeriodicTasks',
]

DJANGO_EASY_AUDIT_UNREGISTERED_URLS_EXTRA = [
    r'^/get_user_notifications/',
]

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
