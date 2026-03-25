# Generated migration for creating default groups

from django.db import migrations


def create_default_groups(apps, schema_editor):
    """
    Cria os grupos padrão do sistema com suas permissões.
    
    Grupos criados:
    - Vendedor: pode criar/editar/deletar/visualizar clientes que ele é responsável
    - Administrador: acesso total ao sistema
    """
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Busca o ContentType do modelo Clients
    try:
        clients_content_type = ContentType.objects.get(app_label='clientes', model='clients')
        notas_content_type = ContentType.objects.get(app_label='clientes', model='notas')
    except ContentType.DoesNotExist:
        # Se os ContentTypes não existem ainda, sair sem erro
        # (isso pode acontecer em migrações fora de ordem)
        return
    
    # ====================================
    # GRUPO: Vendedor
    # ====================================
    grupo_vendedor, created = Group.objects.get_or_create(name='Vendedor')
    
    if created:
        # Permissões para Clients
        perms_clients = Permission.objects.filter(
            content_type=clients_content_type,
            codename__in=['add_clients', 'change_clients', 'view_clients', 'delete_clients']
        )
        grupo_vendedor.permissions.add(*perms_clients)
        
        # Permissões para Notas
        perms_notas = Permission.objects.filter(
            content_type=notas_content_type,
            codename__in=['add_notas', 'change_notas', 'view_notas', 'delete_notas']
        )
        grupo_vendedor.permissions.add(*perms_notas)
        
        print("✓ Grupo 'Vendedor' criado com permissões de clientes e notas")
    else:
        print("✓ Grupo 'Vendedor' já existe")
    
    # ====================================
    # GRUPO: Administrador
    # ====================================
    grupo_admin, created = Group.objects.get_or_create(name='Administrador')
    
    if created:
        # Administrador tem as mesmas permissões do Vendedor
        # A lógica de "acesso total" é controlada pelo código (permissions.py)
        perms_clients = Permission.objects.filter(
            content_type=clients_content_type,
            codename__in=['add_clients', 'change_clients', 'view_clients', 'delete_clients']
        )
        grupo_admin.permissions.add(*perms_clients)
        
        perms_notas = Permission.objects.filter(
            content_type=notas_content_type,
            codename__in=['add_notas', 'change_notas', 'view_notas', 'delete_notas']
        )
        grupo_admin.permissions.add(*perms_notas)
        
        print("✓ Grupo 'Administrador' criado com permissões completas")
    else:
        print("✓ Grupo 'Administrador' já existe")


def remove_default_groups(apps, schema_editor):
    """
    Remove os grupos padrão caso seja necessário reverter a migration.
    """
    Group = apps.get_model('auth', 'Group')
    
    Group.objects.filter(name__in=['Vendedor', 'Administrador']).delete()
    print("✓ Grupos 'Vendedor' e 'Administrador' removidos")


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0003_clients_responsavel'),
        ('auth', '__latest__'),  # Garante que o modelo Group existe
        ('contenttypes', '__latest__'),  # Garante que ContentType existe
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
