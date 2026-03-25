"""
Comando Django para criar grupos padrão do sistema.

Uso:
    python manage.py create_groups
    
Este comando cria os grupos 'Vendedor' e 'Administrador' com suas permissões,
caso ainda não existam.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from clientes.models import Clients, Notas


class Command(BaseCommand):
    help = 'Cria os grupos padrão do sistema: Vendedor e Administrador'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove e recria os grupos (cuidado: remove permissões customizadas)',
        )

    def handle(self, *args, **options):
        """Cria os grupos padrão do sistema com suas permissões."""
        
        if options['reset']:
            self.stdout.write(
                self.style.WARNING('⚠️  Modo RESET ativado - removendo grupos existentes...')
            )
            Group.objects.filter(name__in=['Vendedor', 'Administrador']).delete()
            self.stdout.write(self.style.SUCCESS('✓ Grupos removidos'))
        
        # ContentTypes necessários
        clients_ct = ContentType.objects.get_for_model(Clients)
        notas_ct = ContentType.objects.get_for_model(Notas)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Criando grupos do sistema...'))
        self.stdout.write('='*60 + '\n')
        
        # ====================================
        # GRUPO: Vendedor
        # ====================================
        grupo_vendedor, created = Group.objects.get_or_create(name='Vendedor')
        
        if created or options['reset']:
            # Limpa permissões existentes
            grupo_vendedor.permissions.clear()
            
            # Permissões para Clients
            perms_clients = Permission.objects.filter(
                content_type=clients_ct,
                codename__in=['add_clients', 'change_clients', 'view_clients', 'delete_clients']
            )
            grupo_vendedor.permissions.add(*perms_clients)
            
            # Permissões para Notas
            perms_notas = Permission.objects.filter(
                content_type=notas_ct,
                codename__in=['add_notas', 'change_notas', 'view_notas', 'delete_notas']
            )
            grupo_vendedor.permissions.add(*perms_notas)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Grupo "Vendedor" criado com {grupo_vendedor.permissions.count()} permissões')
            )
            self.stdout.write('  - Pode gerenciar clientes que ele é responsável')
            self.stdout.write('  - Pode gerenciar notas dos seus clientes')
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Grupo "Vendedor" já existe ({grupo_vendedor.permissions.count()} permissões)')
            )
        
        # ====================================
        # GRUPO: Administrador
        # ====================================
        grupo_admin, created = Group.objects.get_or_create(name='Administrador')
        
        if created or options['reset']:
            # Limpa permissões existentes
            grupo_admin.permissions.clear()
            
            # Permissões para Clients
            perms_clients = Permission.objects.filter(
                content_type=clients_ct,
                codename__in=['add_clients', 'change_clients', 'view_clients', 'delete_clients']
            )
            grupo_admin.permissions.add(*perms_clients)
            
            # Permissões para Notas
            perms_notas = Permission.objects.filter(
                content_type=notas_ct,
                codename__in=['add_notas', 'change_notas', 'view_notas', 'delete_notas']
            )
            grupo_admin.permissions.add(*perms_notas)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Grupo "Administrador" criado com {grupo_admin.permissions.count()} permissões')
            )
            self.stdout.write('  - Acesso total a todos os clientes')
            self.stdout.write('  - Acesso total a todas as notas')
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Grupo "Administrador" já existe ({grupo_admin.permissions.count()} permissões)')
            )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ Grupos configurados com sucesso!'))
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write('\n📋 Resumo:')
        self.stdout.write(f'   • Total de grupos: {Group.objects.filter(name__in=["Vendedor", "Administrador"]).count()}/2')
        self.stdout.write(f'   • Vendedor: {grupo_vendedor.permissions.count()} permissões')
        self.stdout.write(f'   • Administrador: {grupo_admin.permissions.count()} permissões\n')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Processo concluído!\n'))
