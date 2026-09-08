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
