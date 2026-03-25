from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class RootViewSet(APIView):
    """
    Healthcheck - Verifica se a API está funcionando

    Endpoint público para monitoramento do status da aplicação.
    Não requer autenticação.
    """

    permission_classes = [AllowAny]  # Público

    @swagger_auto_schema(
        operation_summary="Healthcheck da API",
        operation_description=(
            "Verifica se a API está funcionando corretamente.\n\n"
            "Este endpoint é público e pode ser usado para:\n"
            "- Monitoramento de disponibilidade\n"
            "- Testes de conectividade\n"
            "- Health checks de containers/orquestradores"
        ),
        responses={
            200: openapi.Response(
                description="API funcionando normalmente",
                examples={"application/json": {"system": "ok"}},
            ),
        },
        tags=["healthcheck"],
    )
    def get(self, request, format=None):
        dados = {"system": "ok"}
        return Response(dados)
