from pythondjangoapp.settings.base import *

DEBUG = False

INSTALLED_APPS += (
                   'designthinking.apps.DesignthinkingConfig',
                   'users.apps.UsersConfig',
                    'crispy_forms',
                    'django_cleanup',
                    'rest_framework',
                    'django.contrib.humanize',
                   )
