from drf_spectacular.utils import extend_schema
from config.dashboard import DashboardViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Vendedor
from .serializers import VendedorSerializer
from clientes.models import Cliente
from clientes.serializers import ClienteSerializer


class VendedorViewSet(DashboardViewSet):
    protected_message = 'Este vendedor ainda atende clientes. Reatribua esses clientes antes de excluir.'
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(responses=ClienteSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='clientes')
    def listar_clientes_do_vendedor(self, request, pk=None):
        """
        Rota exigida pelo PDF: /api/vendedores/{id}/clientes/
        Lista todos os clientes atendidos pelo vendedor informado.
        """
        vendedor = self.get_object()
        clientes = Cliente.objects.filter(vendedor=vendedor)
        serializer = ClienteSerializer(clientes, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
