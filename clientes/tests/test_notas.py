"""
Testes de Notas/Interações com Clientes.

Testa:
- Criação de notas associadas a clientes
- Consulta de notas
- Validações de notas
- Permissões de acesso
"""

import pytest
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Clients, Notas


@pytest.mark.django_db
class TestNotasInteracoes(APITestCase):
    """Testes de criação e consulta de notas/interações."""
    
    @classmethod
    def setUpTestData(cls):
        """Cria dados de teste."""
        cls.grupo_vendedor = Group.objects.create(name='Vendedor')
        cls.grupo_admin = Group.objects.create(name='Administrador')
        
        cls.vendedor1 = User.objects.create_user(
            username='vendedor1',
            password='senha123',
            is_staff=True
        )
        cls.vendedor1.groups.add(cls.grupo_vendedor)
        
        cls.vendedor2 = User.objects.create_user(
            username='vendedor2',
            password='senha123',
            is_staff=True
        )
        cls.vendedor2.groups.add(cls.grupo_vendedor)
        
        cls.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        cls.admin.groups.add(cls.grupo_admin)
        
        # Clientes
        cls.cliente1 = Clients.objects.create(
            name='Cliente 1',
            email='cliente1@test.com',
            responsavel=cls.vendedor1
        )
        
        cls.cliente2 = Clients.objects.create(
            name='Cliente 2',
            email='cliente2@test.com',
            responsavel=cls.vendedor2
        )
    
    def test_criar_nota_para_cliente(self):
        """Vendedor cria nota para seu próprio cliente."""
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'Cliente interessado em produto X',
            'client_id': self.cliente1.id
        }
        
        response = self.client.post('/api/v1/notas', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['texto'], 'Cliente interessado em produto X')
        self.assertEqual(response.data['client_name'], 'Cliente 1')
        
        # Verificar no banco
        nota = Notas.objects.get(id=response.data['id'])
        self.assertEqual(nota.client, self.cliente1)
        self.assertEqual(nota.texto, 'Cliente interessado em produto X')
    
    def test_criar_nota_sem_texto(self):
        """Tentar criar nota sem texto (campo obrigatório)."""
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'client_id': self.cliente1.id
        }
        
        response = self.client.post('/api/v1/notas', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('texto', response.data)
    
    def test_criar_nota_sem_cliente(self):
        """Tentar criar nota sem associar a cliente."""
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'Nota sem cliente'
        }
        
        response = self.client.post('/api/v1/notas', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client_id', response.data)
    
    def test_vendedor_nao_pode_criar_nota_para_cliente_de_outro(self):
        """Vendedor não pode criar nota para cliente de outro vendedor."""
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'Tentando criar nota',
            'client_id': self.cliente2.id  # Cliente do vendedor2
        }
        
        response = self.client.post('/api/v1/notas', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client_id', response.data)
    
    def test_listar_notas_vendedor(self):
        """Vendedor lista apenas notas de seus clientes."""
        # Criar notas
        Notas.objects.create(
            texto='Nota do vendedor 1',
            client=self.cliente1
        )
        
        Notas.objects.create(
            texto='Nota do vendedor 2',
            client=self.cliente2
        )
        
        self.client.force_authenticate(user=self.vendedor1)
        
        response = self.client.get('/api/v1/notas')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['texto'], 'Nota do vendedor 1')
    
    def test_listar_notas_admin(self):
        """Admin lista todas as notas."""
        # Criar notas
        Notas.objects.create(
            texto='Nota do vendedor 1',
            client=self.cliente1
        )
        
        Notas.objects.create(
            texto='Nota do vendedor 2',
            client=self.cliente2
        )
        
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get('/api/v1/notas')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_atualizar_nota(self):
        """Vendedor atualiza nota de seu cliente."""
        nota = Notas.objects.create(
            texto='Texto original',
            client=self.cliente1
        )
        
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'Texto atualizado'
        }
        
        response = self.client.patch(
            f'/api/v1/notas/{nota.id}',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['texto'], 'Texto atualizado')
        
        # Verificar no banco
        nota.refresh_from_db()
        self.assertEqual(nota.texto, 'Texto atualizado')
    
    def test_vendedor_nao_pode_atualizar_nota_de_outro(self):
        """Vendedor não pode atualizar nota de cliente de outro vendedor."""
        nota = Notas.objects.create(
            texto='Nota do vendedor2',
            client=self.cliente2
        )
        
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'Tentando atualizar'
        }
        
        response = self.client.patch(
            f'/api/v1/notas/{nota.id}',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_deletar_nota(self):
        """Vendedor deleta nota de seu cliente."""
        nota = Notas.objects.create(
            texto='Nota para deletar',
            client=self.cliente1
        )
        
        self.client.force_authenticate(user=self.vendedor1)
        
        response = self.client.delete(f'/api/v1/notas/{nota.id}')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que foi deletada
        self.assertFalse(Notas.objects.filter(id=nota.id).exists())
    
    def test_multiplas_notas_mesmo_cliente(self):
        """Cliente pode ter múltiplas notas."""
        self.client.force_authenticate(user=self.vendedor1)
        
        # Criar primeira nota
        data1 = {
            'texto': 'Primeira interação',
            'client_id': self.cliente1.id
        }
        response1 = self.client.post('/api/v1/notas', data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Criar segunda nota
        data2 = {
            'texto': 'Segunda interação',
            'client_id': self.cliente1.id
        }
        response2 = self.client.post('/api/v1/notas', data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Verificar que cliente tem 2 notas
        notas = Notas.objects.filter(client=self.cliente1)
        self.assertEqual(notas.count(), 2)
    
    def test_detalhe_nota(self):
        """Ver detalhes de uma nota específica."""
        nota = Notas.objects.create(
            texto='Nota detalhada',
            client=self.cliente1
        )
        
        self.client.force_authenticate(user=self.vendedor1)
        
        response = self.client.get(f'/api/v1/notas/{nota.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['texto'], 'Nota detalhada')
        self.assertEqual(response.data['client_name'], 'Cliente 1')
    
    def test_criar_nota_texto_muito_longo(self):
        """Criar nota com texto muito longo."""
        self.client.force_authenticate(user=self.vendedor1)
        
        data = {
            'texto': 'A' * 5000,  # Texto muito longo
            'client_id': self.cliente1.id
        }
        
        response = self.client.post('/api/v1/notas', data, format='json')
        
        # Deve aceitar ou retornar erro de validação
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_nota_timestamps(self):
        """Verificar que nota tem timestamps de criação e atualização."""
        nota = Notas.objects.create(
            texto='Nota com timestamps',
            client=self.cliente1
        )
        
        self.assertIsNotNone(nota.at_created)
        self.assertIsNotNone(nota.at_updated)
        # Timestamps podem diferir em microsegundos, verificar que são próximos
        time_diff = abs((nota.at_created - nota.at_updated).total_seconds())
        self.assertLess(time_diff, 1.0)  # Menos de 1 segundo de diferença
