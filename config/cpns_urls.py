"""
URL configuration khusus subdomain cpns.agunggumelarsaputra.com.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.cpns.urls', namespace='cpns')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('core/', include('apps.core.urls', namespace='core')),
]
