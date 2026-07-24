from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('moto.urls')),

     # Documentación
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Solo en desarrollo (DEBUG=True): hace que Django sirva los archivos de
# /media/ (fotos de motos, etc.) directamente en /media/..., SIN el
# prefijo "api/" (por eso va acá afuera, y no dentro de moto/urls.py que
# se incluye con ese prefijo). En producción esto no se usa — ahí Nginx
# sirve esos archivos directo, sin pasar por Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)