from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api-auth/', include('rest_framework.urls')),

    # Aplicativos da API
    path('api/', include('clientes.urls')),
    path('api/', include('vendedores.urls')),
]