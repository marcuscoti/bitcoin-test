from django import template

register = template.Library()

@register.inclusion_tag('_form_field.html')
def render_form_field(field):
    """Tag para renderizar os control forms conforme as classes do Bootstrap"""
    return {'field': field}