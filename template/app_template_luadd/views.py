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

{{ old_content }}

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
