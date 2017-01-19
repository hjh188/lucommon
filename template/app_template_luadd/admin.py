from {{ app_name }}.models import ({% for model_name in model_names %}
    {{ model_name }},{% endfor %}
)

from {{ app_name }}.confs import ({% for model_name in model_names %}
    {{ model_name }}Conf,{% endfor %}
)

{{ old_content }}

{% for model_name in model_names %}
class {{ model_name }}Admin(luadmin.MultiDBModelAdmin, CompareVersionAdmin):
    """
    {{ model_name }} admin part
    """
    using = {{ model_name }}Conf.db{% for key1, value1 in admin_field_context.items %}{% if key1 == model_name %}
    # Update `search_fields` for the which field took for search
    search_fields = {{ value1 }}
    # Update `list_display` to show which field display in the admin page
    list_display = {{ value1 }}{% endif %}{% endfor %}

{% endfor %}
{% for model_name in model_names %}
{{ model_name }}._meta.using = {{ model_name }}Conf.db

revisions.register({{ model_name }})

admin.site.register({{ model_name }}, {{ model_name }}Admin){% endfor %}
