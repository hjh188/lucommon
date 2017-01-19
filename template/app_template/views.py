from {{ app_name }}.serializers import ({% for model_name in model_names %}
    {{ model_name }}Serializer,{% endfor %}
)

from {{ app_name }}.models import ({% for model_name in model_names %}
    {{ model_name }},{% endfor %}
)

from {{ app_name }}.confs import ({% for model_name in model_names %}
    {{ model_name }}Conf,{% endfor %}
)

from {{ app_name }}.filters import ({% for model_name in model_names %}
    {{ model_name }}Filter,{% endfor %}
)

from lucommon import (
    viewsets,
)

from lucommon.response import LuResponse
from lucommon.logger import lu_logger

"""
Write less, do more

* By viewsets.ModelViewSet, we can write restful API easily.
Usually, it's necessary to write CRUD operation in the viewset,
it's enough for common scenario. However, we can override
these functions(`list`, `create`, `retrieve`, `update`,
`partial_update`, `destroy`) for more detail control.

Example for HTTP GET:

def retrieve(self, request, *args, **kwargs):
    #`args` indicate the path without ?P(item) in urls route
    #`kwargs` indicate the param in ?P(item) in urls route
    do_something_before()
    response = super(viewsets.ModelViewSet, self).retrieve(request, *args, **kwargs)
    do_something_after()
    return response

* API docs(http://django-rest-swagger.readthedocs.org/en/latest/yaml.html)
Use the YAML Docstring for API docs

"""

{% for model_name in model_names %}
class {{ model_name }}ViewSet(viewsets.LuModelViewSet):
    """
    ViewSet for {{ model_name}} operation
    """
    # Query set
    queryset = {{model_name}}.objects.using({{ model_name }}Conf.db).all()

    # Serializer class
    serializer_class = {{ model_name }}Serializer

    # Filter class
    filter_class = {{ model_name }}Filter

    # Conf class
    conf = {{ model_name }}Conf

    # APP name
    app = "{{ app_name }}"

    # Model name
    model = "{{ model_name }}"

    def perform_create(self, serializer):
        """
        Keep this function for POST db select
        """
        serializer.save(using={{ model_name }}Conf.db)

    def get_queryset(self):
        # Add whatever to filter the response if you want
        return {{ model_name }}.objects.using({{ model_name }}Conf.db).all()


    def list(self, request, *args, **kwargs):
        """
        HTTP GET list entry
        """
        return super({{ model_name }}ViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        HTTP GET item entry
        """
        return super({{ model_name }}ViewSet, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        HTTP POST item entry
        """
        return super({{ model_name }}ViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        HTTP PUT item entry
        """
        return super({{ model_name }}ViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        HTTP PATCH item entry
        """
        return super({{ model_name }}ViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        HTTP DELETE item entry
        """
        return super({{ model_name }}ViewSet, self).destroy(request, *args, **kwargs)

    def history(self, request, *args, **kwargs):
        """
        Object History
        """
        return super({{ model_name }}ViewSet, self).history(request, *args, **kwargs)

{% endfor %}
