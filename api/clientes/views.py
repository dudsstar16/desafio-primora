import sys
from pathlib import Path
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteSerializer

# Permite usar o normalizador de bairros do nosso próprio ETL na busca da API
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.transform_address import canonicalize_neighborhood_name  # noqa: E402


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filterset_fields = ['bairro_normalizado', 'vendedor']

    @action(detail=False, methods=['get'], url_path='bairro/(?P<nome>[^/.]+)')
    def buscar_por_bairro(self, request, nome=None):
        """
        Lista clientes por bairro normalizado.
        Aceita tanto o nome exato ('Águas Claras') quanto variações sem acento
        ou informais ('aguas claras', 'guara ii', 'vte pires') usando a regra do ETL!
        """
        nome_canonico = canonicalize_neighborhood_name(nome or '') or nome
        clientes = Cliente.objects.filter(bairro_normalizado__iexact=nome_canonico)
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='vendedor/(?P<id_vendedor>[^/.]+)')
    def buscar_por_vendedor(self, request, id_vendedor=None):
        """Lista clientes atendidos por um vendedor específico."""
        clientes = Cliente.objects.filter(vendedor_id=id_vendedor)
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)
