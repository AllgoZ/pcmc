# my_middleware.py
class DomainRouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # Extract domain

        if host == 'pcmc.tepros.in':
            request.urlconf = 'pcmc.urls'  # Point to the pcmc app's URL configuration
        elif host in {'globalophthalmicinstitute.org', 'globalophthalmicinstitute.com','www.globalophthalmicinstitute.com','www.globalophthalmicinstitute.org'}:
            request.urlconf = 'goi.urls'  # Point to the global ophthalmic app's URL configuration

        elif host == 'globalophthalmicinstitute.org ':
            request.urlconf = 'goi.urls'  # Point to the global ophthalmic app's URL configuration
        
        elif host == 'globalophthalmicinstitute.com':
            request.urlconf = 'goi.urls'  # Point to the global ophthalmic app's URL configuration

        return self.get_response(request)
