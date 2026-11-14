
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('vendedores.urls')),
    path('api/', include('clientes.urls')),

    path('api/auth/token/', obtain_auth_token),
    path('api-auth/', include('rest_framework.urls')),

    # Documentação da API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
