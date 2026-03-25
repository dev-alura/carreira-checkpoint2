"""
Testes de Autenticação e Autorização.

Testa:
- Login com credenciais válidas e inválidas
- Geração de tokens JWT
- Acesso a rotas protegidas com e sem token
- Tokens expirados ou inválidos
- Refresh tokens
"""

import pytest
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase


@pytest.mark.django_db
class TestAutenticacao(APITestCase):
    """Testes de autenticação e autorização."""
    
    @classmethod
    def setUpTestData(cls):
        """Cria usuários para testes."""
        cls.grupo_vendedor = Group.objects.create(name='Vendedor')
        
        cls.user = User.objects.create_user(
            username='usuario_teste',
            password='senha_correta_123',
            email='usuario@test.com',
            is_staff=True
        )
        cls.user.groups.add(cls.grupo_vendedor)
    
    def test_login_credenciais_validas(self):
        """Login com credenciais válidas retorna tokens."""
        data = {
            'username': 'usuario_teste',
            'password': 'senha_correta_123'
        }
        
        response = self.client.post('/auth/jwt/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(len(response.data['access']) > 0)
    
    def test_login_credenciais_invalidas(self):
        """Login com senha incorreta retorna erro."""
        data = {
            'username': 'usuario_teste',
            'password': 'senha_errada'
        }
        
        response = self.client.post('/auth/jwt/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_usuario_inexistente(self):
        """Login com usuário inexistente retorna erro."""
        data = {
            'username': 'usuario_nao_existe',
            'password': 'qualquer_senha'
        }
        
        response = self.client.post('/auth/jwt/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acesso_rota_protegida_sem_token(self):
        """Tentar acessar rota protegida sem token retorna 401."""
        response = self.client.get('/api/v1/clientes')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acesso_rota_protegida_com_token_valido(self):
        """Acessar rota protegida com token válido retorna sucesso."""
        # Fazer login para obter token
        login_data = {
            'username': 'usuario_teste',
            'password': 'senha_correta_123'
        }
        
        login_response = self.client.post('/auth/jwt/create/', login_data, format='json')
        token = login_response.data['access']
        
        # Usar token para acessar rota protegida
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/clientes')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_acesso_com_token_invalido(self):
        """Tentar acessar com token inválido retorna 401."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token_invalido_123')
        response = self.client.get('/api/v1/clientes')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acesso_sem_bearer_prefix(self):
        """Token sem prefixo Bearer retorna erro."""
        # Obter token válido
        login_data = {
            'username': 'usuario_teste',
            'password': 'senha_correta_123'
        }
        
        login_response = self.client.post('/auth/jwt/create/', login_data, format='json')
        token = login_response.data['access']
        
        # Tentar usar sem "Bearer "
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get('/api/v1/clientes')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token_valido(self):
        """Refresh token válido gera novo access token."""
        # Fazer login
        login_data = {
            'username': 'usuario_teste',
            'password': 'senha_correta_123'
        }
        
        login_response = self.client.post('/auth/jwt/create/', login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Usar refresh token
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post('/auth/jwt/refresh/', refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_token_invalido(self):
        """Refresh token inválido retorna erro."""
        refresh_data = {
            'refresh': 'token_refresh_invalido'
        }
        
        response = self.client.post('/auth/jwt/refresh/', refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_sem_username(self):
        """Tentar login sem username retorna erro."""
        data = {
            'password': 'senha123'
        }
        
        response = self.client.post('/auth/jwt/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_sem_password(self):
        """Tentar login sem password retorna erro."""
        data = {
            'username': 'usuario_teste'
        }
        
        response = self.client.post('/auth/jwt/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_multiplos_logins_mesmo_usuario(self):
        """Múltiplos logins do mesmo usuário geram tokens diferentes."""
        data = {
            'username': 'usuario_teste',
            'password': 'senha_correta_123'
        }
        
        response1 = self.client.post('/auth/jwt/create/', data, format='json')
        token1 = response1.data['access']
        
        response2 = self.client.post('/auth/jwt/create/', data, format='json')
        token2 = response2.data['access']
        
        # Tokens devem ser diferentes
        self.assertNotEqual(token1, token2)
        
        # Ambos devem funcionar
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        response = self.client.get('/api/v1/clientes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        response = self.client.get('/api/v1/clientes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class TestAutorizacaoRotasProtegidas(APITestCase):
    """Testes de autorização em diferentes rotas."""
    
    @classmethod
    def setUpTestData(cls):
        """Cria usuário para testes."""
        cls.grupo_vendedor = Group.objects.create(name='Vendedor')
        
        cls.user = User.objects.create_user(
            username='vendedor',
            password='senha123',
            is_staff=True
        )
        cls.user.groups.add(cls.grupo_vendedor)
    
    def test_endpoints_protegidos_sem_autenticacao(self):
        """Verificar que todos os endpoints principais requerem autenticação."""
        endpoints = [
            '/api/v1/clientes',
            '/api/v1/telefones',
            '/api/v1/notas',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {endpoint} deve requerer autenticação"
            )
    
    def test_post_sem_autenticacao(self):
        """Tentar criar recursos sem autenticação."""
        endpoints_data = [
            ('/api/v1/clientes', {'name': 'Teste', 'email': 'teste@test.com'}),
            ('/api/v1/telefones', {'number': '123456', 'tipo': 'CEL'}),
            ('/api/v1/notas', {'texto': 'Nota teste'}),
        ]
        
        for endpoint, data in endpoints_data:
            response = self.client.post(endpoint, data, format='json')
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"POST em {endpoint} deve requerer autenticação"
            )
