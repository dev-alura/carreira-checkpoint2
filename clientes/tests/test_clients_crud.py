"""
Testes de CRUD e validações de Clientes.

Testa:
- Criação de clientes com dados válidos e inválidos
- Emails duplicados
- Campos obrigatórios
- Validações de formato
"""

import pytest
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Clients


@pytest.mark.django_db
class TestClientesCRUD(APITestCase):
    """Testes de criação, leitura, atualização e exclusão de clientes."""
    
    @classmethod
    def setUpTestData(cls):
        """Cria dados de teste."""
        cls.grupo_vendedor = Group.objects.create(name='Vendedor')
        cls.vendedor = User.objects.create_user(
            username='vendedor_teste',
            password='senha123',
            email='vendedor@test.com',
            is_staff=True
        )
        cls.vendedor.groups.add(cls.grupo_vendedor)
    
    def test_criar_cliente_dados_validos(self):
        """Vendedor cria cliente com dados válidos."""
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'name': 'João Silva',
            'email': 'joao.silva@email.com'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'João Silva')
        self.assertEqual(response.data['email'], 'joao.silva@email.com')
        
        # Verificar no banco
        cliente = Clients.objects.get(email='joao.silva@email.com')
        self.assertEqual(cliente.name, 'João Silva')
        self.assertEqual(cliente.responsavel, self.vendedor)
    
    def test_criar_cliente_email_invalido(self):
        """Tentar criar cliente com email inválido."""
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'name': 'Teste',
            'email': 'email_invalido'  # Email sem @
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_criar_cliente_sem_nome(self):
        """Tentar criar cliente sem nome (campo obrigatório)."""
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'email': 'teste@email.com'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_criar_cliente_sem_email(self):
        """Tentar criar cliente sem email (campo obrigatório)."""
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'name': 'Teste'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_criar_cliente_email_duplicado(self):
        """Tentar criar cliente com email já existente."""
        # Criar primeiro cliente
        Clients.objects.create(
            name='Cliente Existente',
            email='existente@email.com',
            responsavel=self.vendedor
        )
        
        self.client.force_authenticate(user=self.vendedor)
        
        # Tentar criar segundo cliente com mesmo email
        data = {
            'name': 'Cliente Duplicado',
            'email': 'existente@email.com'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_atualizar_cliente(self):
        """Vendedor atualiza seu próprio cliente."""
        cliente = Clients.objects.create(
            name='Nome Original',
            email='original@email.com',
            responsavel=self.vendedor
        )
        
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'name': 'Nome Atualizado',
            'email': 'atualizado@email.com'
        }
        
        response = self.client.patch(
            f'/api/v1/clientes/{cliente.id}',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Nome Atualizado')
        self.assertEqual(response.data['email'], 'atualizado@email.com')
        
        # Verificar no banco
        cliente.refresh_from_db()
        self.assertEqual(cliente.name, 'Nome Atualizado')
    
    def test_deletar_cliente(self):
        """Vendedor deleta seu próprio cliente."""
        cliente = Clients.objects.create(
            name='Cliente para Deletar',
            email='deletar@email.com',
            responsavel=self.vendedor
        )
        
        self.client.force_authenticate(user=self.vendedor)
        
        response = self.client.delete(f'/api/v1/clientes/{cliente.id}')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que foi deletado
        self.assertFalse(Clients.objects.filter(id=cliente.id).exists())
    
    def test_atualizar_cliente_email_duplicado(self):
        """Tentar atualizar cliente para email já existente."""
        # Criar dois clientes
        cliente1 = Clients.objects.create(
            name='Cliente 1',
            email='cliente1@email.com',
            responsavel=self.vendedor
        )
        
        Clients.objects.create(
            name='Cliente 2',
            email='cliente2@email.com',
            responsavel=self.vendedor
        )
        
        self.client.force_authenticate(user=self.vendedor)
        
        # Tentar atualizar cliente1 para email do cliente2
        data = {
            'email': 'cliente2@email.com'
        }
        
        response = self.client.patch(
            f'/api/v1/clientes/{cliente1.id}',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_criar_cliente_nome_muito_longo(self):
        """Tentar criar cliente com nome muito longo."""
        self.client.force_authenticate(user=self.vendedor)
        
        data = {
            'name': 'A' * 300,  # Nome muito longo
            'email': 'teste@email.com'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        # Pode retornar 400 se houver validação de tamanho
        # ou 201 se cortar o nome automaticamente
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])
    
    def test_listar_clientes_vazio(self):
        """Listar clientes quando não há nenhum."""
        self.client.force_authenticate(user=self.vendedor)
        
        response = self.client.get('/api/v1/clientes')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_detalhe_cliente_existente(self):
        """Ver detalhes de um cliente existente."""
        cliente = Clients.objects.create(
            name='Cliente Detalhes',
            email='detalhes@email.com',
            responsavel=self.vendedor
        )
        
        self.client.force_authenticate(user=self.vendedor)
        
        response = self.client.get(f'/api/v1/clientes/{cliente.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Cliente Detalhes')
        self.assertEqual(response.data['email'], 'detalhes@email.com')
    
    def test_detalhe_cliente_inexistente(self):
        """Tentar ver detalhes de cliente que não existe."""
        self.client.force_authenticate(user=self.vendedor)
        
        response = self.client.get('/api/v1/clientes/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
