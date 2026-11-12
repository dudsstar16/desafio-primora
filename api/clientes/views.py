from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    @action(detail=False, methods=['get'], url_path='bairro/(?P<nome>[^/.]+)')
    def buscar_por_bairro(self, request, nome=None):
        clientes = Cliente.objects.filter(bairro_normalizado__iexact=nome)
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='vendedor/(?P<id_vendedor>[^/.]+)')
    def buscar_por_vendedor(self, request, id_vendedor=None):
        clientes = Cliente.objects.filter(vendedor_id=id_vendedor)
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)