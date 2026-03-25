from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from clientes.models import Clients, Notas, Phone
from clientes.serializers import ClientesSerializer, NotasSerializer, PhoneSerializer
from crm_api.permissions import (
    IsClientOwnerOrAdmin,
    IsRelatedClientOwnerOrAdmin,
    is_admin_user,
)


class ClientsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsClientOwnerOrAdmin]
    serializer_class = ClientesSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name", "email", "responsavel"]
    search_fields = ["name", "email"]

    def get_queryset(self):
        """
        Filtra clientes baseado no responsável:
        - Administrador: vê todos os clientes
        - Vendedor: só vê clientes que ele é responsável
        """
        user = self.request.user

        if is_admin_user(user):
            # Admin vê todos
            return Clients.objects.all().select_related("responsavel")
        else:
            # Vendedor só vê seus clientes
            return Clients.objects.filter(responsavel=user).select_related(
                "responsavel"
            )

    def perform_create(self, serializer):
        """
        Auto-atribui responsável ao criar cliente:
        - Vendedor: auto-atribui a si mesmo
        - Admin: pode escolher ou deixar vazio (usa self se não especificado)
        """
        if "responsavel" not in serializer.validated_data or not is_admin_user(
            self.request.user
        ):
            # Vendedor sempre é atribuído automaticamente
            # Admin sem especificar também é auto-atribuído
            serializer.save(responsavel=self.request.user)
        else:
            # Admin especificou o responsável
            serializer.save()

    def perform_update(self, serializer):
        """
        Previne vendedor de alterar o responsável
        """
        if not is_admin_user(self.request.user):
            # Remove responsavel dos dados validados se vendedor tentar alterar
            serializer.validated_data.pop("responsavel", None)
        serializer.save()


class PhoneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsRelatedClientOwnerOrAdmin]
    serializer_class = PhoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["tipo", "client", "client__responsavel"]
    search_fields = [
        "client__name",
        "client__email",
        "number",
    ]

    def get_queryset(self):
        """
        Filtra telefones baseado no responsável do cliente:
        - Administrador: vê todos
        - Vendedor: só vê telefones de seus clientes
        """
        user = self.request.user

        if is_admin_user(user):
            return Phone.objects.all().select_related("client", "client__responsavel")
        else:
            return Phone.objects.filter(client__responsavel=user).select_related(
                "client", "client__responsavel"
            )


class NotasViewSet(viewsets.ModelViewSet):
    permission_classes = [IsRelatedClientOwnerOrAdmin]
    serializer_class = NotasSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["client", "client__responsavel"]
    search_fields = [
        "texto",
        "client__name",
    ]

    def get_queryset(self):
        """
        Filtra notas baseado no responsável do cliente:
        - Administrador: vê todas
        - Vendedor: só vê notas de seus clientes
        """
        user = self.request.user

        if is_admin_user(user):
            return Notas.objects.all().select_related("client", "client__responsavel")
        else:
            return Notas.objects.filter(client__responsavel=user).select_related(
                "client", "client__responsavel"
            )
