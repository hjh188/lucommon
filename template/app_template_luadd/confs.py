{{old_content}}

{% for model_name in model_names %}
class {{ model_name }}Conf(LuConf):
    """
    It's a good practice to write {{ model_name }}
    related setting here.
    """
    # In a real world, you mostly need to change db here
    db = 'default'

    # Generate the default SEARCH for the model by lu SQL injection
    sql_injection_map = {'get_{{ model_name | lower }}':'SELECT LU_RESPONSE_FIELD FROM {{ app_name }}_{{ model_name | lower }} WHERE LU_SEARCH_CONDITION'}

{% endfor %}
