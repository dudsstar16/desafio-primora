from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from vendedores.models import Vendedor
from .models import Cliente


class ClienteAPITests(APITestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="admin_teste",
            password="senha_teste_123",
        )
        self.vendedor = Vendedor.objects.create(nome_vendedor="Bruno Almeida")

        self.cliente1 = Cliente.objects.create(
            id_cliente="CLI0001",
            razao_social="Mercadinho Boa Vista",
            cnpj_normalizado="84959310341316",
            telefone_normalizado="61970855700",
            email="contato@mercadinhobo.com.br",
            bairro_normalizado="Águas Claras",
            cep_normalizado="71926750",
            cidade="Brasília",
            uf="DF",
            data_cadastro_normalizado="2022-06-21",
            vendedor=self.vendedor,
        )

        self.lista_url = reverse("cliente-list")
        self.detalhe_url = reverse("cliente-detail", args=[self.cliente1.id_cliente])

    def test_listar_clientes_publico_get(self):
        resp = self.client.get(self.lista_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id_cliente"], "CLI0001")

    def test_filtrar_clientes_por_bairro_com_ou_sem_acento(self):
        # Busca sem acento ('aguas claras') deve encontrar 'Águas Claras' graças à integração com o ETL!
        resp = self.client.get("/api/clientes/bairro/aguas claras/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["bairro_normalizado"], "Águas Claras")

    def test_filtrar_clientes_por_vendedor_nas_duas_rotas(self):
        # Rota 1: /api/clientes/vendedor/{id}/
        resp1 = self.client.get(f"/api/clientes/vendedor/{self.vendedor.id_vendedor}/")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp1.data), 1)

        # Rota 2: /api/vendedores/{id}/clientes/
        resp2 = self.client.get(f"/api/vendedores/{self.vendedor.id_vendedor}/clientes/")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp2.data), 1)

    def test_visitante_nao_logado_nao_pode_criar_cliente(self):
        resp = self.client.post(self.lista_url, {"id_cliente": "CLI9999"}, format="json")
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_usuario_logado_pode_criar_atualizar_e_excluir_cliente(self):
        self.client.force_authenticate(user=self.usuario)

        novo_payload = {
            "id_cliente": "CLI0002",
            "razao_social": "Comercial São Judas",
            "cnpj_normalizado": "04711671902294",
            "telefone_normalizado": "61953862084",
            "email": "contato@comercialsao.com.br",
            "bairro_normalizado": "Taguatinga",
            "cep_normalizado": "72140010",
            "cidade": "Brasília",
            "uf": "DF",
            "data_cadastro_normalizado": "2023-10-07",
            "vendedor_id": self.vendedor.id_vendedor,
        }
        resp_post = self.client.post(self.lista_url, novo_payload, format="json")
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        # Confirma que zero à esquerda no CNPJ foi preservado como texto
        self.assertEqual(resp_post.data["cnpj_normalizado"], "04711671902294")

        # Documentação Redoc acessível
        resp_docs = self.client.get("/api/docs/")
        self.assertEqual(resp_docs.status_code, status.HTTP_200_OK)
