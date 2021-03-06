# -*- coding: utf-8 -*-

from .base import *

DEBUG = True

TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'db.devel.sqlite3'),
    }
}


INSTALLED_APPS += (
    'devserver',
)
