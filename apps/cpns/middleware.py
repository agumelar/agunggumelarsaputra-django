from django.conf import settings
from django.shortcuts import redirect


class CpnsSubdomainMiddleware:
    """
    Mengarahkan request dari subdomain cpns.* (mis. cpns.agunggumelarsaputra.com atau cpns.localhost)
    ke apps.cpns.urls secara transparan.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host.startswith('cpns.'):
            request.urlconf = 'config.cpns_urls'
            request.is_cpns_subdomain = True
        else:
            request.is_cpns_subdomain = False

        return self.get_response(request)


class PesertaHanyaCpnsMiddleware:
    """
    Peserta CPNS publik hanya boleh memakai CPNS Hub. Di situs sekolah (host utama)
    peserta dialihkan ke dasbor CPNS, kecuali ke jalur cpns, keluar, OAuth, dan berkas statis.
    """
    JALUR_BOLEH = ('/cpns/', '/accounts/logout/', '/accounts/oauth/', '/static/', '/media/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (
            user is not None
            and user.is_authenticated
            and user.is_peserta
            and not getattr(request, 'is_cpns_subdomain', False)
            and not request.path.startswith(self.JALUR_BOLEH)
        ):
            return redirect(settings.CPNS_URL + 'dasbor/')
        return self.get_response(request)
