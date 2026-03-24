
from django.contrib import admin
from django.urls import path, include
from django.conf import settings               # <--- 1. NUEVO: Importar configuración
from django.conf.urls.static import static     # <--- 2. NUEVO: Importar función estática

from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

# 3. NUEVO: AGREGAR ESTO AL FINAL
# Esto le dice a Django: "Si estamos probando (DEBUG), permite ver las fotos de la carpeta media"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)