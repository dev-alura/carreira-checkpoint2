"""
Views customizadas para gerenciamento de usuários
"""
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


class UserManagementViewSet(viewsets.ViewSet):
    """
    Gerenciamento de Usuários
    
    Endpoints para administração de usuários do sistema:
    - POST /api/v1/users/create/ → Admin cria novo usuário
    - GET  /api/v1/users/list/   → Admin lista todos os usuários
    - GET  /api/v1/users/me/     → Usuário vê seus próprios dados
    """
    
    @swagger_auto_schema(
        operation_summary="Criar novo usuário (Admin)",
        operation_description=(
            "Endpoint restrito para administradores criarem novos usuários no sistema.\n\n"
            "**Permissão necessária:** Apenas administradores (is_staff=True).\n\n"
            "**Campos obrigatórios:** username, password"
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Nome de usuário único",
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email do usuário",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Senha do usuário",
                ),
                "first_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Primeiro nome",
                ),
                "last_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Sobrenome",
                ),
                "is_staff": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Define se o usuário é um administrador",
                    default=False,
                ),
            },
            example={
                "username": "novo_usuario",
                "email": "usuario@email.com",
                "password": "senha123",
                "first_name": "João",
                "last_name": "Silva",
                "is_staff": False,
            },
        ),
        responses={
            201: openapi.Response(
                description="Usuário criado com sucesso",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "novo_usuario",
                        "email": "usuario@email.com",
                        "first_name": "João",
                        "last_name": "Silva",
                        "is_staff": False,
                    }
                },
            ),
            400: "Dados inválidos ou usuário já existe",
            401: "Não autenticado",
            403: "Sem permissão (apenas admins)",
        },
        tags=["Usuários"],
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create(self, request):
        """
        Endpoint para ADMIN criar novo usuário
        
        Exemplo:
        POST /api/v1/users/create/
        {
            "username": "novo_usuario",
            "email": "usuario@email.com",
            "password": "senha123",
            "first_name": "Nome",
            "last_name": "Sobrenome"
        }
        """
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        is_staff = request.data.get("is_staff", False)
        
        if not username or not password:
            return Response(
                {"error": "username e password são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Usuário já existe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff
        )
        
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Listar todos os usuários (Admin)",
        operation_description=(
            "Retorna a lista completa de todos os usuários cadastrados no sistema.\n\n"
            "**Permissão necessária:** Apenas administradores (is_staff=True)."
        ),
        responses={
            200: openapi.Response(
                description="Lista de usuários",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@email.com",
                            "first_name": "Administrador",
                            "last_name": "Sistema",
                            "is_staff": True,
                            "is_active": True,
                            "date_joined": "2024-01-01T10:00:00Z",
                        },
                        {
                            "id": 2,
                            "username": "usuario",
                            "email": "usuario@email.com",
                            "first_name": "Usuário",
                            "last_name": "Teste",
                            "is_staff": False,
                            "is_active": True,
                            "date_joined": "2024-01-15T14:30:00Z",
                        },
                    ]
                },
            ),
            401: "Não autenticado",
            403: "Sem permissão (apenas admins)",
        },
        tags=["Usuários"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def list(self, request):
        """
        Endpoint para ADMIN listar todos os usuários
        
        GET /api/v1/users/list/
        """
        users = User.objects.all()
        users_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
            for user in users
        ]
        return Response(users_data)
    
    @swagger_auto_schema(
        operation_summary="Ver meus dados (Usuário autenticado)",
        operation_description=(
            "Retorna os dados do usuário atualmente autenticado.\n\n"
            "**Permissão necessária:** Qualquer usuário autenticado.\n\n"
            "Útil para verificar informações do próprio perfil."
        ),
        responses={
            200: openapi.Response(
                description="Dados do usuário autenticado",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "usuario",
                        "email": "usuario@email.com",
                        "first_name": "João",
                        "last_name": "Silva",
                        "is_staff": False,
                        "date_joined": "2024-01-15T14:30:00Z",
                    }
                },
            ),
            401: "Não autenticado",
        },
        tags=["Usuários"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para usuário ver seus próprios dados
        
        GET /api/v1/users/me/
        """
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
            }
        )
