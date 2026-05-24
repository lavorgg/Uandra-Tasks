import json
from django import template

register = template.Library()

@register.filter
def tojson(valor):
    return json.dumps(valor)
