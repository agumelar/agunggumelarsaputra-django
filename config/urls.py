"""
URL configuration for agunggumelarsaputra-django project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('pembelajaran/', include('apps.pembelajaran.urls', namespace='pembelajaran')),
    path('tka/', include('apps.tka.urls', namespace='tka')),
    path('literasi/', include('apps.literasi.urls', namespace='literasi')),
    path('gamification/', include('apps.gamification.urls', namespace='gamification')),
    path('panel-guru/', include('apps.admin_panel.urls', namespace='admin_panel')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
