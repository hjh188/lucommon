from {{ app_name }}.views import ({% for model_name in model_names %}
    {{ model_name }}ViewSet,{% endfor %}
)

{{ old_content }}

urlpatterns += [{% for model_name in model_names %}
    url(r'^{{ model_name|lower }}s/$', {{ model_name }}ViewSet.as_view({'get':'list',
                                        'post': 'create'})),
    url(r'^{{ model_name|lower }}s/(?P<pk>[0-9]+)$', {{ model_name }}ViewSet.as_view({'get':'retrieve',
                                                      'put': 'update',
                                                      'patch': 'partial_update',
                                                      'delete': 'destroy'})),
    url(r'^{{ model_name|lower }}s/(?P<pk>[0-9]+)/history$', {{ model_name }}ViewSet.as_view({'get':'history'})),
{% endfor %}
]
