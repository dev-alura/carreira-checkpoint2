from django.contrib import admin

from clientes.models import Clients, Notas, Phone
from crm_api.permissions import is_admin_user


class Clientes(admin.ModelAdmin):
    list_display = ("id", "name", "email", "responsavel", "at_created", "at_updated")
    list_display_links = ("id", "name")
    list_per_page = 100
    list_filter = ("responsavel",)
    search_fields = ("name", "email", "responsavel__username")
    autocomplete_fields = ["responsavel"]

    def get_queryset(self, request):
        """
        Filtra clientes baseado no usuário:
        - Admin/Superuser: vê todos
        - Vendedor: só vê seus clientes
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_admin_user(request.user):
            return qs
        # Vendedor só vê seus clientes
        return qs.filter(responsavel=request.user)

    def get_readonly_fields(self, request, obj=None):
        """
        Vendedor não pode alterar o responsável
        """
        if request.user.is_superuser or is_admin_user(request.user):
            return []
        return ["responsavel"]

    def save_model(self, request, obj, form, change):
        """
        Auto-atribui responsável ao criar cliente se não for especificado
        """
        if not change and not obj.responsavel_id:
            obj.responsavel = request.user
        super().save_model(request, obj, form, change)


class Phones(admin.ModelAdmin):
    list_display = ("id", "number", "tipo", "client", "get_responsavel")
    list_filter = ("tipo", "client__responsavel")
    search_fields = ("number", "client__name", "client__responsavel__username")
    autocomplete_fields = ["client"]

    @admin.display(description="Responsável")
    def get_responsavel(self, obj):
        return obj.client.responsavel.username if obj.client else "-"

    def get_queryset(self, request):
        """
        Vendedor só vê telefones de seus clientes
        """
        qs = (
            super()
            .get_queryset(request)
            .select_related("client", "client__responsavel")
        )
        if request.user.is_superuser or is_admin_user(request.user):
            return qs
        return qs.filter(client__responsavel=request.user)


class NotasAdmin(admin.ModelAdmin):
    list_display = ("id", "texto_resumo", "client", "get_responsavel", "at_created")
    list_filter = ("client__responsavel", "at_created")
    search_fields = ("texto", "client__name", "client__responsavel__username")
    autocomplete_fields = ["client"]

    @admin.display(description="Texto")
    def texto_resumo(self, obj):
        return obj.texto[:50] + "..." if len(obj.texto) > 50 else obj.texto

    @admin.display(description="Responsável")
    def get_responsavel(self, obj):
        return obj.client.responsavel.username if obj.client else "-"

    def get_queryset(self, request):
        """
        Vendedor só vê notas de seus clientes
        """
        qs = (
            super()
            .get_queryset(request)
            .select_related("client", "client__responsavel")
        )
        if request.user.is_superuser or is_admin_user(request.user):
            return qs
        return qs.filter(client__responsavel=request.user)


admin.site.register(Clients, Clientes)
admin.site.register(Phone, Phones)
admin.site.register(Notas, NotasAdmin)
