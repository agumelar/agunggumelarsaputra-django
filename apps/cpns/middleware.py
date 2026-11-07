from django.conf import settings
from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse


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
    Peserta CPNS publik hanya boleh memakai CPNS Hub.

    Di host utama peserta dialihkan ke dasbor CPNS, kecuali ke jalur cpns, keluar,
    OAuth, dan berkas statis. Di host cpns rute situs sekolah ikut terpasang
    (config/cpns_urls.py), jadi path di-resolve: selain namespace cpns dan jalur
    umum di atas, peserta dialihkan ke dasbor cpns. Path yang tidak dikenal
    dibiarkan lewat agar tetap 404.
    """
    JALUR_UMUM = ('/accounts/logout/', '/accounts/oauth/', '/static/', '/media/')
    JALUR_BOLEH = ('/cpns/',) + JALUR_UMUM

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and user.is_peserta:
            if getattr(request, 'is_cpns_subdomain', False):
                if not self._boleh_di_host_cpns(request):
                    return redirect(reverse('cpns:dasbor', urlconf=request.urlconf))
            elif not request.path.startswith(self.JALUR_BOLEH):
                return redirect(settings.CPNS_URL + 'dasbor/')
        return self.get_response(request)

    def _boleh_di_host_cpns(self, request):
        if request.path_info.startswith(self.JALUR_UMUM):
            return True
        try:
            cocok = resolve(request.path_info, urlconf=request.urlconf)
        except Resolver404:
            return True
        return cocok.namespaces[:1] == ['cpns']
