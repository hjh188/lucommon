#!/usr/bin/env python

from django.conf import settings

"""
Settings for lucommon APP

We will do two things here:
1. move dependency from project setting to lucommon,
   other people just need to import lucommon in project
   setting, no need to care others

2. setting also works from lucommon itself
"""

# Add additional APPS
INSTALLED_APPS = settings.INSTALLED_APPS

INSTALLED_APPS += ('django_logging',
                   'rest_framework',
                   'rest_framework_swagger',
                   'corsheaders',
                   'rest_framework_extensions',
                   'reversion',
                   'reversion_compare',
                   'django_mysql',
                   'lucommon')

# For reversion
ADD_REVERSION_ADMIN=True

# Add additional MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES += ('django_logging.middleware.DjangoLoggingMiddleware',
                       'corsheaders.middleware.CorsMiddleware',
                       'lucommon.middleware.response.LuResponseFormatMiddleware',
                       'lucommon.middleware.request.LuRequireLoginMiddleware',
                       'lucommon.middleware.profiler.ProfileMiddleware',
                       'lucommon.middleware.response.LuUserCookie',
                       'crum.CurrentRequestUserMiddleware')

# DISABLE_CSRF_CHECK need to be set before import lucommon in project settings
DISABLE_CSRF_CHECK = False if not hasattr(settings, 'DISABLE_CSRF_CHECK') else settings.DISABLE_CSRF_CHECK

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('lucommon.middleware.request.LuDisableCSRF',) if DISABLE_CSRF_CHECK else MIDDLEWARE_CLASSES


ROOT_URLCONF = settings.ROOT_URLCONF
# Logger setting
# Custom Use
"""
1. To log debug messages:
>>> from django_logging import log
>>> log.debug('debug message')

2. To log handled exceptions:
>>> from django_logging import log, ErrorLogObject
>>> log.error(ErrorLogObject(request, exception))
"""

DJANGO_LOGGING = {
    "CONSOLE_LOG": False,
    "SQL_LOG": False,
    "LOG_LEVEL": "INFO",
}


# For rest framework settings
REST_FRAMEWORK = {
    'URL_FORMAT_OVERRIDE': 'lu_format',

    #'DEFAULT_RENDERER_CLASSES': (
    #    'rest_framework.renderers.JSONRenderer',
    #    'rest_framework.renderers.BrowsableAPIRenderer',
    #    'rest_framework_xml.renderers.XMLRenderer',
    #    'rest_framework_yaml.renderers.YAMLRenderer',
    #),
    #'DEFAULT_PARSER_CLASSES': (
    #    'rest_framework.parsers.JSONParser',
    #    'rest_framework_xml.parsers.XMLParser',
    #    'rest_framework_yaml.parsers.YAMLParser',
    #),
}

APP_DEBUG=True

# Cross-Origin Resource Sharing
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)
CORS_EXPOSE_HEADERS = ()

# For Model search
SEARCH_ENABLE = True
SEARCH_PARAM = 'lu_search_word'
SEARCH_PARAM_DELIMITER = ','
SEARCH_PARAM_IN_DELIMITER = '|'
SEARCH_PARAM_NOTIN_DELIMITER = '|'
SEARCH_KEY = 'lu_search_field'
SEARCH_KEY_DELIMITER = ','
SEARCH_KEY_OR_DELIMITER = '|'
SEARCH_TYPE = 'lu_search_type'
SEARCH_TYPE_DELIMITER = ','

# For Group
GROUP_PARAM = 'lu_group_field'
GROUP_PARAM_DELIMITER = ','

# For Response
RESPONSE_FIELD = 'lu_response_field'
RESPONSE_FIELD_DELIMITER = ','
RESPONSE_MODE = 'lu_response_mode'
# Debug mode would be useful by leveraging rest framework debug page
RESPONSE_DEBUG_MODE = '0'
RESPONSE_DISTINCT = 'lu_response_distinct'

# For Order
ORDERING_ENABLE = True
ORDERING_PARAM = 'lu_order_field'
ORDERING_PARAM_DELIMITER = ','

# Other
AGGREGATE_DISTINCT = 'lu_aggregate_distinct'

DATE_TYPE = 'lu_date_format'

# Pagination
LIMIT_FIELD = 'lu_limit'
OFFSET_FIELD = 'lu_offset'
DEFAULT_LIMIT = 10
MAX_LIMIT = 10000
UNLIMIT = '-1'

# Auth and Permission
AUTH = True
PERM = False
# Rest LOGIN_URL to disalbe login required redirect
# App could set this value in project settings
LOGIN_URL = None

LOGIN_REQUIRED_URLS = []
LOGIN_REQUIRED_URLS_EXCEPTIONS = [
    r'(.*)/login(.*)$',
    r'(.*)/logout/(.*)$',
    r'(.*)/docs/(.*)$',
    r'(.*)/admin/(.*)$',
]

# For SQL injection
SQL_TEXT = 'lu_sql'
SQL_PARAM = 'lu_sql_param'
SQL_SEARCH_CONDITION = 'lu_sql_search_condition'

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_KEY_FUNC':
      'lucommon.cache.default_api_key_func',
    'DEFAULT_ETAG_FUNC':
      'lucommon.cache.default_api_key_func',
}


