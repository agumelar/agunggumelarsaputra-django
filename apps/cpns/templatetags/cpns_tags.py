from django import template

register = template.Library()


@register.filter
def kurang(ambang, skor):
    """Selisih poin yang masih kurang dari ambang; 0 jika sudah tercapai."""
    try:
        return max(int(ambang) - int(skor), 0)
    except (TypeError, ValueError):
        return 0
