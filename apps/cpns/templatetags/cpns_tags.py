from django import template

register = template.Library()


@register.filter
def kurang(ambang, skor):
    """Selisih poin yang masih kurang dari ambang; 0 jika sudah tercapai."""
    try:
        return max(int(ambang) - int(skor), 0)
    except (TypeError, ValueError):
        return 0


@register.filter
def persen_dari(nilai, maks):
    """Persen nilai terhadap maks, dibatasi 0..100 untuk lebar bar."""
    try:
        return max(0, min(100, round(int(nilai) * 100 / int(maks))))
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
