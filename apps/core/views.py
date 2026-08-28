from django.shortcuts import render


def home_view(request):
    """
    Landing page utama personal website & vocational learning hub.
    Mendukung partial swap HTMX jika request berasal dari HTMX boost / tab.
    """
    context = {
        'active_nav': 'home',
    }
    return render(request, 'core/home.html', context)
