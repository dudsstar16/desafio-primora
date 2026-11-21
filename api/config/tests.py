from django.core.management import get_commands
from django.contrib.auth import get_user_model
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
        self.seller = seller
        self.customer = client

    def login_with_token(self):
        get_user_model().objects.create_user(username='operadora', password='senha-teste')
        response = self.client.post('/api/auth/token/', {
            'username': 'operadora', 'password': 'senha-teste',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_public_and_authenticated_contacts_on_all_customer_routes(self):
        routes = [
            '/api/clientes/', '/api/clientes/CLI0002/',
            '/api/clientes/bairro/Taguatinga/',
            f'/api/clientes/vendedor/{self.seller.pk}/',
            f'/api/vendedores/{self.seller.pk}/clientes/',
        ]
        fields = ('cnpj_normalizado', 'telefone_normalizado', 'email')
        for authenticated in (False, True):
            if authenticated:
                self.login_with_token()
            expected = (('28327648350305', '61953862084', 'contato@example.com')
                        if authenticated else ('************05', '*******2084', 'c***@example.com'))
            for route in routes:
                with self.subTest(route=route, authenticated=authenticated):
                    response = self.client.get(route)
                    self.assertEqual(response.status_code, 200)
                    row = response.data[0] if isinstance(response.data, list) else response.data
                    self.assertEqual(tuple(row[field] for field in fields), expected)
                    self.assertIn('no-store', response['Cache-Control'])

    def test_me_requires_valid_token(self):
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalido')
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        self.client.credentials()
        self.login_with_token()
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'username': 'operadora', 'can_write': True})

    def test_protected_records_and_unlinked_customer(self):
        self.login_with_token()
        for route in ('/api/clientes/CLI0002/', f'/api/vendedores/{self.seller.pk}/'):
            with self.subTest(route=route):
                response = self.client.delete(route)
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response.data['code'], 'protected_relation')
                self.assertEqual(response.data['related_count'], 1)
                self.assertTrue(response.data['detail'])
        self.assertTrue(AuditoriaEtl.objects.filter(cliente=self.customer).exists())
        self.customer.pk = 'NOVO'
        self.customer.save(force_insert=True)
        self.assertEqual(self.client.delete('/api/clientes/NOVO/').status_code, 204)
        self.assertFalse(Cliente.objects.filter(pk='NOVO').exists())

    def test_health_is_public_and_minimal(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'status': 'ok', 'database': 'available'})

    def test_bootstrap_command_is_discoverable(self):
        self.assertIn('bootstrap_primora', get_commands())

    def test_metrics_are_aggregated_and_public(self):
        response = self.client.get('/api/apresentacao/metricas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['totals']['clients'], 1)
        self.assertEqual(response.data['totals']['corrected_conflicts'], 1)
        self.assertEqual(response.data['neighborhoods'][0], {'name': 'Taguatinga', 'count': 1})
        self.assertNotContains(response, 'valor_original')
        self.assertNotContains(response, 'valor_tratado')
