from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import AuditoriaEtl, Cliente
from vendedores.models import Vendedor


class PresentationEndpointsTests(APITestCase):
    def setUp(self):
        seller = Vendedor.objects.create(nome_vendedor='Bruno Almeida')
        client = Cliente.objects.create(
            id_cliente='CLI0002', razao_social='Comercial São Judas',
            cnpj_normalizado='28327648350305', telefone_normalizado='61953862084',
            email='contato@example.com', bairro_normalizado='Taguatinga',
            cep_normalizado='72140010', cidade='Brasília', uf='DF',
            data_cadastro_normalizado='2023-10-07', vendedor=seller,
        )
        AuditoriaEtl.objects.create(
            cliente=client, campo_afetado='bairro', valor_original='Sul (Águas Claras)',
            valor_tratado='Taguatinga',
            regra_aplicada='GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO',
            data_processamento=timezone.now(),
        )

    def test_health_is_public_and_minimal(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'ok', 'database': 'available'})

    def test_metrics_are_aggregated_and_public(self):
        response = self.client.get('/api/apresentacao/metricas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['totals']['clients'], 1)
        self.assertEqual(response.data['totals']['corrected_conflicts'], 1)
        self.assertEqual(response.data['neighborhoods'][0], {'name': 'Taguatinga', 'count': 1})
        self.assertNotContains(response, 'valor_original')
        self.assertNotContains(response, 'valor_tratado')
