from django.contrib.auth.models import User
from rest_framework import serializers

from clientes.models import Clients, Notas, Phone
from crm_api.permissions import is_admin_user


class ResponsavelSerializer(serializers.ModelSerializer):
    """Serializer para exibir dados do responsável"""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class ClientesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = ["name"]


class PhoneSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Clients.objects.all(), source="client", write_only=True
    )

    class Meta:
        model = Phone
        fields = ["id", "number", "tipo", "client_id", "client_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        # Filtra clientes disponíveis baseado no usuário
        if request and hasattr(request, "user"):
            if not is_admin_user(request.user):
                # Vendedor só pode criar telefones para seus clientes
                self.fields["client_id"].queryset = Clients.objects.filter(
                    responsavel=request.user
                )


class NotasSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Clients.objects.all(), source="client", write_only=True
    )

    class Meta:
        model = Notas
        fields = ["id", "texto", "client_id", "client_name", "at_created", "at_updated"]
        read_only_fields = ["id", "at_created", "at_updated"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        # Filtra clientes disponíveis baseado no usuário
        if request and hasattr(request, "user"):
            if not is_admin_user(request.user):
                # Vendedor só pode criar notas para seus clientes
                self.fields["client_id"].queryset = Clients.objects.filter(
                    responsavel=request.user
                )


class NotasListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notas
        fields = ["texto", "at_created"]


class PhoneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ["tipo", "number"]


class ClientesSerializer(serializers.ModelSerializer):
    telefones = PhoneListSerializer(many=True, required=False)
    notas = NotasListSerializer(many=True, required=False)
    responsavel = ResponsavelSerializer(read_only=True)
    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="responsavel",
        write_only=True,
        required=False,
        help_text="ID do vendedor responsável (apenas para admin)",
    )

    class Meta:
        model = Clients
        fields = [
            "id",
            "name",
            "email",
            "responsavel",
            "responsavel_id",
            "telefones",
            "notas",
            "at_created",
            "at_updated",
        ]
        read_only_fields = ["id", "at_created", "at_updated"]

    def get_fields(self):
        """
        Customiza campos baseado no tipo de usuário:
        - Vendedor: responsavel_id é removido (não pode escolher)
        - Admin: responsavel_id disponível para escolha
        """
        fields = super().get_fields()
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            # Se não é admin, remove o campo responsavel_id
            if not is_admin_user(request.user):
                fields.pop("responsavel_id", None)

        return fields

    def create(self, validated_data):
        """
        Cria o cliente e seus telefones de forma aninhada
        """
        telefones_data = validated_data.pop("telefones", [])
        notas_data = validated_data.pop("notas", [])

        # Cria o cliente
        cliente = Clients.objects.create(**validated_data)

        # Cria os telefones associados
        for telefone_data in telefones_data:
            Phone.objects.create(client=cliente, **telefone_data)

        # Cria as notas associadas
        for nota_data in notas_data:
            Notas.objects.create(client=cliente, **nota_data)

        return cliente

    def update(self, instance, validated_data):
        """
        Atualiza o cliente e seus telefones
        """
        telefones_data = validated_data.pop("telefones", None)
        notas_data = validated_data.pop("notas", None)

        # Atualiza os campos do cliente
        instance.name = validated_data.get("name", instance.name)
        instance.email = validated_data.get("email", instance.email)
        
        # Atualiza o responsável se fornecido (apenas admin pode)
        if "responsavel" in validated_data:
            instance.responsavel = validated_data.get("responsavel")
        
        instance.save()

        # Se telefones foram fornecidos, atualiza
        if telefones_data is not None:
            # Remove telefones antigos
            instance.telefones.all().delete()

            # Cria novos telefones
            for telefone_data in telefones_data:
                Phone.objects.create(client=instance, **telefone_data)

        if notas_data is not None:
            # Remove notas antigas
            instance.notas.all().delete()

            # Cria novas notas
            for nota_data in notas_data:
                Notas.objects.create(client=instance, **nota_data)

        return instance
