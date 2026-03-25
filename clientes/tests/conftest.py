"""
Configurações compartilhadas para pytest.
"""

import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Permite acesso ao banco de dados em todos os testes."""
    pass


@pytest.fixture
def api_client():
    """Cliente de API para testes."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def vendedor_user(db):
    """Cria um usuário vendedor para testes."""
    from django.contrib.auth.models import Group, User
    
    grupo = Group.objects.get_or_create(name='Vendedor')[0]
    user = User.objects.create_user(
        username='vendedor_fixture',
        password='senha123',
        is_staff=True
    )
    user.groups.add(grupo)
    return user


@pytest.fixture
def admin_user(db):
    """Cria um usuário admin para testes."""
    from django.contrib.auth.models import Group, User
    
    grupo = Group.objects.get_or_create(name='Administrador')[0]
    user = User.objects.create_user(
        username='admin_fixture',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    user.groups.add(grupo)
    return user
