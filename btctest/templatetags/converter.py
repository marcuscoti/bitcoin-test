from django import template

register = template.Library()

@register.filter
def to_btc(value):
    """Filter para converter satoshis em btc no template"""
    value = float(value) / 100000000
    value = format(value, ".9f")
    return value