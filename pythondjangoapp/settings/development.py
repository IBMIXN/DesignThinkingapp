from pythondjangoapp.settings.base import *

DEBUG = True

INSTALLED_APPS += (
                   'designthinking.apps.DesignthinkingConfig',
                   'users.apps.UsersConfig',
                    'crispy_forms',
                    'django_cleanup',
                    'rest_framework',
                    'django.contrib.humanize',
                   )
