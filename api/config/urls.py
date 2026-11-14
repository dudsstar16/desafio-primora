from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação via Token
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api-auth/', include('rest_framework.urls')),

    # Documentação Interativa OpenAPI (Redoc e Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Aplicativos da API (Clientes e Vendedores)
    path('api/', include('clientes.urls')),
    path('api/', include('vendedores.urls')),
]
