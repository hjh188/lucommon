from django.conf.urls import url

from {{ app_name }}.views import ({% for model_name in model_names %}
    {{ model_name }}ViewSet,{% endfor %}
)


"""
Lucommon didn't use the Router class to register url,
Actually we set urls explicitly, one point is to control
what method we want to expose clearly.

By default, we set CURD and patch update. Please modify according
to your project
"""

urlpatterns = [{% for model_name in model_names %}
    url(r'^{{ model_name|lower }}s/$', {{ model_name }}ViewSet.as_view({'get':'list',
                                        'post': 'create'})),
    url(r'^{{ model_name|lower }}s/(?P<pk>[0-9]+)$', {{ model_name }}ViewSet.as_view({'get':'retrieve',
                                                      'put': 'update',
                                                      'patch': 'partial_update',
                                                      'delete': 'destroy'})),
    url(r'^{{ model_name|lower }}s/(?P<pk>[0-9]+)/history$', {{ model_name }}ViewSet.as_view({'get':'history'})),
{% endfor %}
]


