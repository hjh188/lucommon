import copy

from django.core import urlresolvers

from lucommon.code import LuCode
from lucommon.response import LuResponse
from lucommon import settings

"""
Format response
"""

class ResponseFormatMiddlewareBase(object):
    """
    Base for response format
    """
    def in_whitelist(self, request, response):
        # Check for the whitelist case and return directly

        # case 1: for the `lu_mode` == '0', lucommon return directly
        # which it's useful for the rest framework debugger page
        if settings.RESPONSE_MODE in request.GET:
            if request.GET.get(settings.RESPONSE_MODE) == '0':
                return True

        # case 2: if request is for swagger page, return direclty
        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
        resolver_match = resolver.resolve(request.path)
        if resolver_match.func.__name__ in \
              ('SwaggerUIView', 'SwaggerApiView','SwaggerResourcesView',):
            return True

        # Other case: if no data for response, return directly
        if not hasattr(response, 'data'):
            return True

        return False

    def process_template_response(self, request, response):
        raise NotImplemented('Need to implement in subclass!')


class LuResponseFormatMiddleware(ResponseFormatMiddlewareBase):
    """
    Refer to Lu reponse output:
    http://lujs.cn/confluence/display/tester/API+Respone+Format
    """

    def process_template_response(self, request, response):
        # Process response
        if self.in_whitelist(request, response):
            return response

        _data = copy.deepcopy(response.data)

        _message = response.data['message'] if isinstance(response.data, dict) and 'message' in response.data else ''

        _data = None if response.exception else _data

        _code = response.code if hasattr(response, 'code') and response.code is not None else response.status_code

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

            if response.pagination:
                response.data['pagination'] = response.pagination

            return response

        # Codec for the code and message
        codec = LuCode(response.status_code)
        response.data['code'] = codec.code
        response.data['message'] = codec.message if not response.data['message'] else response.data['message']

        return response


class LuUserCookie(object):
    """
    Set username to cookie
    """
    def process_response(self, request, response):
        if request.user.is_authenticated() and not request.COOKIES.get('username'):
            response.set_cookie("username", request.user.username)
        elif not request.user.is_authenticated() and request.COOKIES.get('username'):
            response.delete_cookie("username")

        return response

