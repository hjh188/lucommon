from {{ app_name }}.models import ({% for model_name in model_names %}
    {{ model_name }},{% endfor %}
)

{{ old_content }}

{% for model_name in model_names %}
class {{ model_name }}Filter(django_filters.FilterSet):
    """
    {{ model_name }} filter
    """{% for key1, value1 in filter_context.items %}{% if key1 == model_name %}{% for key2, value2 in value1.items %}
    {{ key2 }} = {{ value2 }}{% endfor %}{% endif %}{% endfor %}

    class Meta:
        model = {{ model_name }}{% for key1, value1 in filter_field_context.items %}{% if key1 == model_name %}
        fields = {{ value1 }}{% endif %}{% endfor %}

{% endfor %}
