"""
Teste para verificar se URLs com e sem trailing slash funcionam.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestTrailingSlash:
    """Testa se ambas URLs (com/sem barra) funcionam"""

    def test_url_sem_trailing_slash(self):
        """Testa URL sem barra final: /api/v1/clientes"""
        # Criar usuário vendedor
        user = User.objects.create_user(
            username="vendedor_test", password="test123", is_staff=True
        )
        vendedor_group, _ = user.groups.get_or_create(name="vendedor")
        user.groups.add(vendedor_group)

        # Autenticar
        client = APIClient()
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Testar URL sem barra
        response = client.get("/api/v1/clientes")
        assert response.status_code == 200, (
            f"Esperado 200, recebeu {response.status_code}"
        )

    def test_url_com_trailing_slash(self):
        """Testa URL COM barra final: /api/v1/clientes/"""
        # Criar usuário vendedor
        user = User.objects.create_user(
            username="vendedor_test2", password="test123", is_staff=True
        )
        vendedor_group, _ = user.groups.get_or_create(name="vendedor")
        user.groups.add(vendedor_group)

        # Autenticar
        client = APIClient()
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Testar URL COM barra (deve funcionar por causa do middleware)
        response = client.get("/api/v1/clientes/")
        assert response.status_code == 200, (
            f"Esperado 200, recebeu {response.status_code}"
        )

    def test_ambas_urls_retornam_mesma_resposta(self):
        """Verifica que ambas URLs retornam os mesmos dados"""
        # Criar usuário vendedor
        user = User.objects.create_user(
            username="vendedor_test3", password="test123", is_staff=True
        )
        vendedor_group, _ = user.groups.get_or_create(name="vendedor")
        user.groups.add(vendedor_group)

        # Autenticar
        client = APIClient()
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Testar ambas
        response_sem_barra = client.get("/api/v1/clientes")
        response_com_barra = client.get("/api/v1/clientes/")

        assert response_sem_barra.status_code == 200
        assert response_com_barra.status_code == 200
        assert response_sem_barra.json() == response_com_barra.json()
