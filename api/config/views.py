from django.db import connection
from django.db.models import Count
from django.views.decorators.cache import never_cache
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from clientes.models import AuditoriaEtl, Cliente
from vendedores.models import Vendedor


@extend_schema_view(post=extend_schema(auth=[], description='Troca usuário e senha por um token DRF.'))
class DashboardTokenView(ObtainAuthToken):
    pass


@extend_schema(responses={
    200: inline_serializer('DashboardUser', fields={
        'username': serializers.CharField(), 'can_write': serializers.BooleanField(),
    }),
    401: OpenApiResponse(description='Token ausente ou inválido.'),
})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@never_cache
def current_user(request):
    """Valida o token do painel e informa quem pode manter os cadastros."""
    return Response({'username': request.user.get_username(), 'can_write': True})


@extend_schema(responses=inline_serializer('Health', fields={
    'status': serializers.CharField(), 'database': serializers.CharField(),
}))
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Sinal mínimo de saúde, sem detalhes internos do ambiente."""
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        cursor.fetchone()
    return Response({'status': 'ok', 'database': 'available'})


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(['GET'])
@permission_classes([AllowAny])
def presentation_metrics(request):
    """Agregados seguros para a apresentação; nunca expõe linhas da auditoria."""
    neighborhoods = list(
        Cliente.objects.values('bairro_normalizado')
        .annotate(total=Count('id_cliente'))
        .order_by('-total', 'bairro_normalizado')
    )
    sellers = list(
        Vendedor.objects.annotate(total=Count('clientes'))
        .values('id_vendedor', 'nome_vendedor', 'total')
        .order_by('-total', 'nome_vendedor')
    )
    audit_fields = list(
        AuditoriaEtl.objects.values('campo_afetado')
        .annotate(total=Count('id_auditoria'))
        .order_by('-total', 'campo_afetado')
    )
    conflict_count = AuditoriaEtl.objects.filter(
        regra_aplicada__icontains='GUARDRAIL_CONFLITO'
    ).values('cliente_id').distinct().count()

    return Response({
        'source': 'database',
        'totals': {
            'clients': Cliente.objects.count(),
            'sellers': Vendedor.objects.count(),
            'audit_changes': AuditoriaEtl.objects.count(),
            'corrected_conflicts': conflict_count,
        },
        'neighborhoods': [
            {'name': item['bairro_normalizado'], 'count': item['total']}
            for item in neighborhoods
        ],
        'sellers': [
            {'id': item['id_vendedor'], 'name': item['nome_vendedor'], 'count': item['total']}
            for item in sellers
        ],
        'audit_by_field': [
            {'field': item['campo_afetado'], 'count': item['total']}
            for item in audit_fields
        ],
    })
