#!/usr/bin/env python

import copy

from lucommon.code import LuCode
from lucommon.response import LuResponse
from django.conf import settings

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

"""
Lu common Decorator util
"""

def format_response(func):
    """
    Refer to Lu reponse output:
    http://lujs.cn/confluence/display/tester/API+Respone+Format
    """
    def _wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        # Store the data firstly
        _data = copy.deepcopy(response.data)

        _message = response.data['message'] if isinstance(response.data, dict) and 'message' in response.data else ''

        _data = None if response.exception else _data

        _code = response.code if hasattr(response, 'code') and response.code else response.status_code

        response.data = {
                         'code': _code,
                         'message': _message,
                         'data': _data,
                        }

        # Process for the paging info
        if isinstance(_data, dict) and 'pagination' in _data:
            response.data['pagination'] = _data.pop('pagination')
            response.data['data'] = _data.pop('data')

        # Check if the response is instance of LuResponse
        # LuResponse no need for http codec
        if isinstance(response, LuResponse):
            response.data['code'] = response.code if response.code else response.data['code']
            response.data['message'] = response.message if response.message else response.data['message']

            return response

        # Codec for the code and message
        codec = LuCode(response.status_code)
        response.data['code'] = codec.code
        response.data['message'] = codec.message if not response.data['message'] else response.data['message']

        return response

    return _wrapper


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Import from django, we will add settings here:
    if settings.LOGIN_URL is not set, do nothing here

    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    if not settings.LOGIN_URL:
        return function

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


