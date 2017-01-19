#!/usr/bin/env python

# UnicodeDecodeError: 'ascii' codec can't 
#decode byte 0xe2 in position 195: ordinal not in range
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

try:
    from django.conf import settings
    if hasattr(settings, 'INSTALLED_APPS'):
        from .settings import *
except ImportError:
    pass

