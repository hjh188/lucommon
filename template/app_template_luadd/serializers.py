from {{ app_name }}.models import ({% for model_name in model_names %}
    {{ model_name }},{% endfor %}
)

{{ old_content }}

{% for model_name in model_names %}
class {{ model_name }}Serializer(serializers.LuModelSerializer):
    """
    {{ model_name }} Serializer
    """
    class Meta:
        model = {{ model_name }}
        fields = '__all__'

{% endfor %}
