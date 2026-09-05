import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdownify')
def markdownify(value):
    """
    Renders markdown text into clean HTML with support for tables,
    fenced code blocks, definition lists, line breaks, and clean formatting.
    """
    if not value:
        return ""
    html = markdown.markdown(
        value,
        extensions=[
            'extra',
            'nl2br',
            'sane_lists',
        ]
    )
    return mark_safe(html)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Retrieves an item from a dictionary or object using variable key.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

