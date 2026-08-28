from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter untuk mengambil value dari dictionary berdasarkan key.
    Contoh penggunaan: {{ mydict|get_item:item.id }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
