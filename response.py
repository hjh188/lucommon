#!/usr/bin/env python

from rest_framework.response import Response

"""
Lu `Response` inherit from rest framework Response
"""

class LuResponse(Response):
    """
    Custom code and message
    """
    def __init__(self, data=None, status=None,
                 code=None, message=None, pagination=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        super(LuResponse, self).__init__(data=data, status=status,
                                         template_name=template_name, headers=headers,
                                         exception=exception, content_type=content_type)
        self.code = code
        self.message = message
        self.pagination = pagination


