from lucommon import serializers

from {{ app_name }}.models import ({% for model_name in model_names %}
    {{ model_name }},{% endfor %}
)

"""
Serializers allow complex data such as querysets and model instances to be converted 
to native Python datatypes that can then be easily rendered into JSON, XML or 
other content types. Serializers also provide deserialization, allowing parsed data
to be converted back into complex types, after first validating the incoming data.

The serializers in REST framework work very similarly to Django's Form and ModelForm classes.
We provide a Serializer class which gives you a powerful, generic way to control the output of your responses,
as well as a ModelSerializer class which provides a useful shortcut for creating serializers that deal with model instances and querysets.


In this serializer class, we can do data validation, control the response items, etc.

Besides Meta data below `model`, you can use others like `fields`, `exclude`, etc.
you can get full and depth understanding from the docs here:
http://www.django-rest-framework.org/api-guide/serializers/
"""

{% for model_name in model_names %}
class {{ model_name }}Serializer(serializers.LuModelSerializer):
    """
    {{ model_name }} Serializer
    """
    class Meta:
        model = {{ model_name }}
        fields = '__all__'

{% endfor %}
