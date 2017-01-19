#!/usr/bin/env python

"""
Filter for rest framework

Add user customed filter here
"""
import operator
from django.db import models
from django.utils import six
from rest_framework import filters
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.compat import (
    crispy_forms, distinct, django_filters, guardian, template_render
)

#from lucommon import settings
from django.conf import settings


class BaseFilter(object):
    """
    Just copy django filter_queryset function here
    """
    class SEARCH_TYPE:
        contain = '0'
        start = '1'
        exact = '2'
        re = '3'
        count = '4'
        max = '5'
        min = '6'
        avg = '7'
        _in = '8'
        _not_in = '9'

    search_type_map = {
        '0': '', # Contain match
        '1': '^', # Starts-with search
        '2': '=', # Exact matches
        '3': '$', # Regex search
        '4': 'count', # Aggregate function Count
        '5': 'max', # Aggregate function Max
        '6': 'min', # Aggregate function Min
        '7': 'avg', # Aggregate fucntion Avg
    }

    aggregate_distinct = '1'

    response_distinct = '1'

    def filter_queryset(self, queryset):
        queryset = self.queryset

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        return queryset


class LuDefaultCustomFilter(BaseFilter):
    """
    CustomFilter more like based on code level filter

    Override `filter_queryset` defined in GenericAPIView
    """
    def filter_search_by_request_query_params(self, request, queryset=None):
        """
        Would be useful if you call outside of rest framework filters

        for the model item filter, leverage LuSearchFilter

        Return: QuerySet
        """
        _queryset = self.queryset if queryset is None else queryset

        return LuSearchFilter().filter_queryset(request, _queryset, self)

    def filter_by_request_query_params(self, request, queryset=None):
        """
        Would be useful if you call outside of rest framework filters

        for the model item filter

        Return: QuerySet
        """
        _queryset = self.queryset if queryset is None else queryset

        return filters.DjangoFilterBackend().filter_queryset(request, _queryset, self)

    def filter_by_request_query_params_order(self, request, queryset=None):
        """
        Would be useful if you call outside of rest framework ordering filters

        Return QuerySet
        """
        _queryset = self.queryset if queryset is None else queryset

        return filters.OrderingFilter().filter_queryset(request, _queryset, self)

    def filter_queryset(self, queryset):
        queryset = super(LuDefaultCustomFilter, self).filter_queryset(queryset)

        # Mapping begin and end to created_at
        if 'begin' in self.request.query_params:
            begin = '%sT00:00:00' % self.request.query_params.get('begin')
            queryset = queryset.filter(created_at__gte=begin)
        if 'end' in self.request.query_params:
            end = '%sT23:59:59' % self.request.query_params.get('end')
            queryset = queryset.filter(created_at__lte=end)

        #####################
        # Add more if needs #
        #####################

        return queryset


class LuSearchFilter(SearchFilter):
    """
    For search filter
    """
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = getattr(view, 'search_words', None)
        search_terms = search_terms if search_terms else self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        #orm_lookups = [
        #    self.construct_search(six.text_type(search_field))
        #    for search_field in search_fields
        #]
        # Add sub or operation
        orm_lookups = []
        for search_field in search_fields:
            search_field_list = search_field.split(settings.SEARCH_KEY_OR_DELIMITER)

            if len(search_field_list) == 1:
                # keep old
                orm_lookups.append(self.construct_search(six.text_type(search_field)))
            else:
                if search_field[0] in ('$','^','='):
                    for i, item in enumerate(search_field_list[1:]):
                        search_field_list[i+1] = search_field[0] + search_field_list[i+1]

                or_orm_lookups = [
                    self.construct_search(six.text_type(item))
                    for item in search_field_list
                ]
                orm_lookups.append(or_orm_lookups)

        base = queryset
        # Process for multiple search field
        if request.query_params.get(settings.SEARCH_KEY):
            for index, orm_lookup in enumerate(orm_lookups):
                try:
                    search_term = search_terms[index]
                except:
                    search_term = ''

                if isinstance(orm_lookup, list):
                    queries = [models.Q(**{sub_orm_lookup: search_term}) for sub_orm_lookup in orm_lookup]
                else:
                    queries = [models.Q(**{orm_lookup: search_term}),]

                queryset = queryset.filter(reduce(operator.or_, queries))
        else:
            # Keep full text search if not search field specified
            for search_term in search_terms:
                queries = [
                    models.Q(**{orm_lookup: search_term})
                    for orm_lookup in orm_lookups
                ]
                queryset = queryset.filter(reduce(operator.or_, queries))

        # Filtering against a many-to-many field requires us to
        # call queryset.distinct() in order to avoid duplicate items
        # in the resulting queryset.
        return distinct(queryset, base)


class LuOrderingFilter(OrderingFilter):
    """
    For order filter
    """
    def get_ordering(self, request, queryset, view):
        """
        Lu won't do fields validation!
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(settings.ORDERING_PARAM_DELIMITER)]
            #ordering = self.remove_invalid_fields(queryset, fields, view)
            ordering = fields
            if ordering:
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)


