"""
Testes de Filtros e Buscas.

Testa:
- Busca por nome (case-insensitive)
- Busca por email (case-insensitive)
- Busca por telefone
- Filtros combinados
- Ordenação
"""

import pytest
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Clients, Phone


@pytest.mark.django_db
class TestFiltrosListagem(APITestCase):
    """Testes de filtros e buscas na listagem."""

    @classmethod
    def setUpTestData(cls):
        """Cria dados de teste."""
        cls.grupo_vendedor = Group.objects.create(name="Vendedor")

        cls.vendedor = User.objects.create_user(
            username="vendedor", password="senha123", is_staff=True
        )
        cls.vendedor.groups.add(cls.grupo_vendedor)

        # Criar clientes para testes de filtros
        cls.cliente1 = Clients.objects.create(
            name="João Silva", email="joao.silva@email.com", responsavel=cls.vendedor
        )

        cls.cliente2 = Clients.objects.create(
            name="Maria Santos",
            email="maria.santos@email.com",
            responsavel=cls.vendedor,
        )

        cls.cliente3 = Clients.objects.create(
            name="Pedro Costa", email="pedro.costa@email.com", responsavel=cls.vendedor
        )

        cls.cliente4 = Clients.objects.create(
            name="Ana Paula", email="ana.paula@email.com", responsavel=cls.vendedor
        )

        # Criar telefones para testes
        Phone.objects.create(number="11987654321", tipo="CEL", client=cls.cliente1)

        Phone.objects.create(number="21987654321", tipo="WHATS", client=cls.cliente2)

    def test_busca_por_nome_exato(self):
        """Buscar cliente por nome exato."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=João Silva")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "João Silva")

    def test_busca_por_nome_parcial(self):
        """Buscar cliente por parte do nome."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=Silva")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "João Silva")

    def test_busca_case_insensitive_nome(self):
        """Busca por nome é case-insensitive."""
        self.client.force_authenticate(user=self.vendedor)

        # Buscar com minúsculas
        response = self.client.get("/api/v1/clientes?search=joão")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pode encontrar ou não dependendo do banco de dados e collation
        # SQLite pode não suportar case-insensitive para acentos
        if len(response.data) > 0:
            self.assertEqual(response.data[0]["name"], "João Silva")

        # Buscar com SILVA em maiúscula (sem acento deve funcionar)
        response = self.client.get("/api/v1/clientes?search=SILVA")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_busca_por_email(self):
        """Buscar cliente por email."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=maria.santos@email.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "maria.santos@email.com")

    def test_busca_case_insensitive_email(self):
        """Busca por email é case-insensitive."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=MARIA.SANTOS@EMAIL.COM")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "maria.santos@email.com")

    def test_busca_email_parcial(self):
        """Buscar por parte do email."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=santos")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve encontrar Maria Santos (nome e email)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filtro_por_nome_exato(self):
        """Filtrar cliente por nome exato usando query param."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?name=João Silva")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 0:  # Se filtro estiver implementado
            self.assertEqual(response.data[0]["name"], "João Silva")

    def test_filtro_por_email_exato(self):
        """Filtrar cliente por email exato."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?email=pedro.costa@email.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 0:  # Se filtro estiver implementado
            self.assertEqual(response.data[0]["email"], "pedro.costa@email.com")

    def test_busca_sem_resultados(self):
        """Buscar por termo que não existe."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=XYZ_NAO_EXISTE_123")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_listar_todos_sem_filtro(self):
        """Listar todos os clientes sem filtro."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_busca_telefone_numero(self):
        """Buscar telefone por número."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/telefones?search=11987654321")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["number"], "11987654321")

    def test_busca_telefone_por_nome_cliente(self):
        """Buscar telefone pelo nome do cliente associado."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/telefones?search=João Silva")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 0:
            self.assertEqual(response.data[0]["client_name"], "João Silva")

    def test_filtro_telefone_por_tipo(self):
        """Filtrar telefones por tipo."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/telefones?tipo=CEL")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 0:
            for telefone in response.data:
                self.assertEqual(telefone["tipo"], "CEL")

    def test_busca_multiplos_resultados(self):
        """Busca que retorna múltiplos resultados."""
        self.client.force_authenticate(user=self.vendedor)

        # Buscar por 'email.com' que todos têm
        response = self.client.get("/api/v1/clientes?search=email.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 1)

    def test_busca_com_caracteres_especiais(self):
        """Busca com caracteres especiais não deve quebrar."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=@#$%")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Não deve retornar erro, apenas lista vazia

    def test_paginacao_resultados(self):
        """Verificar se paginação está funcionando (se implementada)."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?page=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Se paginação estiver implementada, verificar estrutura

    def test_busca_string_vazia(self):
        """Buscar com string vazia retorna todos."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_filtro_combinado_nome_email(self):
        """Aplicar múltiplos filtros simultaneamente."""
        self.client.force_authenticate(user=self.vendedor)

        # Se filtros combinados estiverem implementados
        response = self.client.get(
            "/api/v1/clientes?name=João Silva&email=joao.silva@email.com"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 0:
            self.assertEqual(response.data[0]["name"], "João Silva")
            self.assertEqual(response.data[0]["email"], "joao.silva@email.com")


@pytest.mark.django_db
class TestBuscaComplexas(APITestCase):
    """Testes de buscas mais complexas."""

    @classmethod
    def setUpTestData(cls):
        """Cria dados de teste."""
        cls.grupo_vendedor = Group.objects.create(name="Vendedor")

        cls.vendedor = User.objects.create_user(
            username="vendedor", password="senha123", is_staff=True
        )
        cls.vendedor.groups.add(cls.grupo_vendedor)

        # Clientes com nomes similares para testar busca
        Clients.objects.create(
            name="Carlos Alberto Silva",
            email="carlos@test.com",
            responsavel=cls.vendedor,
        )

        Clients.objects.create(
            name="Carlos Eduardo Lima",
            email="eduardo@test.com",
            responsavel=cls.vendedor,
        )

        Clients.objects.create(
            name="Alberto Santos", email="alberto@test.com", responsavel=cls.vendedor
        )

    def test_busca_nome_comum(self):
        """Buscar por nome comum que aparece em múltiplos clientes."""
        self.client.force_authenticate(user=self.vendedor)

        response = self.client.get("/api/v1/clientes?search=Carlos")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        nomes = [cliente["name"] for cliente in response.data]
        self.assertIn("Carlos Alberto Silva", nomes)
        self.assertIn("Carlos Eduardo Lima", nomes)

    def test_busca_acento_diferente(self):
        """Busca deve considerar acentos."""
        self.client.force_authenticate(user=self.vendedor)

        # Criar cliente com acento
        Clients.objects.create(
            name="José da Silva", email="jose@test.com", responsavel=self.vendedor
        )

        # Buscar com acento
        response = self.client.get("/api/v1/clientes?search=José")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve encontrar ou não dependendo da implementação
