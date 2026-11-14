from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Vendedor
from .serializers import VendedorSerializer
from clientes.models import Cliente
from clientes.serializers import ClienteSerializer


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path='clientes')
    def listar_clientes_do_vendedor(self, request, pk=None):
        """
        Rota exigida pelo PDF: /api/vendedores/{id}/clientes/
        Lista todos os clientes atendidos pelo vendedor informado.
        """
        vendedor = self.get_object()
        clientes = Cliente.objects.filter(vendedor=vendedor)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)
