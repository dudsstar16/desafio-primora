
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from .models import Vendedor


class VendedorAPITests(APITestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="usuario_teste",
            password="senha_teste_123"
        )

        self.vendedor = Vendedor.objects.create(
            nome_vendedor="Ana Silva"
        )

        self.lista_url = reverse("vendedor-list")
        self.detalhe_url = reverse(
            "vendedor-detail",
            args=[self.vendedor.id_vendedor]
        )

    def test_listar_vendedores_sem_autenticacao(self):
        resposta = self.client.get(self.lista_url)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_200_OK
        )

    def test_cadastrar_vendedor_autenticado(self):
        self.client.force_authenticate(user=self.usuario)

        resposta = self.client.post(
            self.lista_url,
            {"nome_vendedor": "Carlos Souza"},
            format="json"
        )

        self.assertEqual(
            resposta.status_code,
            status.HTTP_201_CREATED
        )
        self.assertTrue(
            Vendedor.objects.filter(
                nome_vendedor="Carlos Souza"
            ).exists()
        )

    def test_consultar_vendedor_por_id(self):
        resposta = self.client.get(self.detalhe_url)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            resposta.data["nome_vendedor"],
            "Ana Silva"
        )

    def test_atualizar_vendedor_autenticado(self):
        self.client.force_authenticate(user=self.usuario)

        resposta = self.client.put(
            self.detalhe_url,
            {"nome_vendedor": "Ana Silva Atualizada"},
            format="json"
        )

        self.assertEqual(
            resposta.status_code,
            status.HTTP_200_OK
        )

        self.vendedor.refresh_from_db()
        self.assertEqual(
            self.vendedor.nome_vendedor,
            "Ana Silva Atualizada"
        )

    def test_excluir_vendedor_autenticado(self):
        self.client.force_authenticate(user=self.usuario)

        resposta = self.client.delete(self.detalhe_url)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(
            Vendedor.objects.filter(
                id_vendedor=self.vendedor.id_vendedor
            ).exists()
        )

    def test_visitante_nao_pode_cadastrar(self):
        resposta = self.client.post(
            self.lista_url,
            {"nome_vendedor": "Vendedor Não Autorizado"},
            format="json"
        )

        self.assertIn(
            resposta.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

    def test_visitante_nao_pode_atualizar(self):
        resposta = self.client.put(
            self.detalhe_url,
            {"nome_vendedor": "Nome Alterado"},
            format="json"
        )

        self.assertIn(
            resposta.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

    def test_visitante_nao_pode_excluir(self):
        resposta = self.client.delete(self.detalhe_url)

        self.assertIn(
            resposta.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )
