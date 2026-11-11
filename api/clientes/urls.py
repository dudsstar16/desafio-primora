from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Registre aqui a ViewSet de Clientes (ex: router.register(r'clientes', ClienteViewSet, basename='cliente'))

urlpatterns = [
    *router.urls,
]
