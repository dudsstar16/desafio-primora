from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import DashboardTokenView, current_user, health, presentation_metrics

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoints públicos, somente leitura, usados pelo site de apresentação
    path('api/health/', health, name='api-health'),
    path('api/apresentacao/metricas/', presentation_metrics, name='presentation-metrics'),

    # Autenticação via Token
    path('api/auth/token/', DashboardTokenView.as_view(), name='api_token_auth'),
    path('api/auth/me/', current_user, name='dashboard-user'),
    path('api-auth/', include('rest_framework.urls')),

    # Documentação Interativa OpenAPI (Redoc e Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Aplicativos da API (Clientes e Vendedores)
    path('api/', include('clientes.urls')),
    path('api/', include('vendedores.urls')),
]
