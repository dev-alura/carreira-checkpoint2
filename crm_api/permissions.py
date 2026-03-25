"""
Permissões customizadas para o CRM API
"""

from rest_framework import permissions


def is_admin_user(user):
    """
    Verifica se o usuário é Administrador:
    - Pertence ao grupo 'Administrador', OU
    - É superuser
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name='Administrador').exists()


def is_vendedor_user(user):
    """
    Verifica se o usuário é Vendedor:
    - Pertence ao grupo 'Vendedor'
    """
    return user.groups.filter(name='Vendedor').exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para qualquer usuário autenticado,
    mas apenas admins podem criar/editar/deletar.
    """

    def has_permission(self, request, view):
        # Qualquer usuário autenticado pode ler (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Apenas admins podem criar/editar/deletar
        return request.user and is_admin_user(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite que usuários vejam/editem apenas seus próprios dados,
    mas admins podem ver/editar tudo.
    """

    def has_object_permission(self, request, view, obj):
        # Admins podem tudo
        if is_admin_user(request.user):
            return True

        # Usuário pode ver/editar apenas seus próprios dados
        return obj == request.user or obj.id == request.user.id


class IsClientOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão para clientes:
    - Administrador: pode ver/editar todos os clientes
    - Vendedor: só pode ver/editar clientes onde ele é o responsável
    
    Usado em ClientsViewSet
    """
    
    def has_permission(self, request, view):
        # Usuário precisa estar autenticado
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Administrador pode tudo
        if is_admin_user(request.user):
            return True
        
        # Vendedor só pode acessar clientes que ele é o responsável
        if is_vendedor_user(request.user):
            return obj.responsavel == request.user
        
        # Se não é admin nem vendedor, nega acesso
        return False


class IsRelatedClientOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão para telefones e notas:
    - Administrador: pode ver/editar todos
    - Vendedor: só pode ver/editar telefones/notas de clientes que ele é responsável
    
    Usado em PhoneViewSet e NotasViewSet
    """
    
    def has_permission(self, request, view):
        # Usuário precisa estar autenticado
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Administrador pode tudo
        if is_admin_user(request.user):
            return True
        
        # Vendedor só pode acessar telefones/notas de clientes que ele é responsável
        if is_vendedor_user(request.user):
            return obj.client.responsavel == request.user
        
        # Se não é admin nem vendedor, nega acesso
        return False
