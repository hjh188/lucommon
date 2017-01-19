#!/usr/bin/env python

from rest_framework import pagination
from rest_framework.response import Response

from rest_framework.utils.urls import remove_query_param, replace_query_param

from lucommon import settings

class LuPagination(pagination.LimitOffsetPagination):
    """
    Custom for the pagnination output
    """
    limit_query_param = settings.LIMIT_FIELD
    offset_query_param = settings.OFFSET_FIELD
    default_limit = settings.DEFAULT_LIMIT
    max_limit = settings.MAX_LIMIT
    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.count,
             },
            'data': data
        })

class LuPagination2(pagination.LimitOffsetPagination):
    """
    NO format for output
    """
    limit_query_param = settings.LIMIT_FIELD
    offset_query_param = settings.OFFSET_FIELD
    default_limit = settings.DEFAULT_LIMIT
    max_limit = settings.MAX_LIMIT

def get_next_link(request, limit, offset, count):
    if offset + limit >= count or count is None:
        return None

    url = request.build_absolute_uri()
    url = replace_query_param(url, settings.LIMIT_FIELD, limit)

    offset = offset + limit
    return replace_query_param(url, settings.OFFSET_FIELD, offset)

def get_previous_link(request, limit, offset, count):
    if offset <= 0 or count is None:
        return None

    url = request.build_absolute_uri()
    url = replace_query_param(url, settings.LIMIT_FIELD, limit)

    if offset - limit <= 0:
        return remove_query_param(url, settings.OFFSET_FIELD)

    offset = offset - limit
    return replace_query_param(url, settings.OFFSET_FIELD, offset)


