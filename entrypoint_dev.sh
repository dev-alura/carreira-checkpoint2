#!/bin/bash
set -euo pipefail # Sai imediatamente se um comando falhar, falha se variável não definida, falha em pipe de comandos
echo "Iniciando Startup...."
echo "Aplicando migrações..."
uv run python manage.py migrate --noinput
echo ""
echo ">> Criando grupos de acesso..."
uv run python manage.py create_groups
echo ""
echo "Coletando arquivos estáticos..."
uv run python manage.py collectstatic --noinput
echo ""
#Criando Superuser
echo ">> Creating superuser if not exists..."
uv run python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    # Adiciona o superuser ao grupo Administrador
    admin_group = Group.objects.get(name='Administrador')
    user.groups.add(admin_group)
    print("Superuser created and added to 'Administrador' group")
else:
    user = User.objects.get(username=username)
    # Garante que o superuser está no grupo Administrador
    admin_group = Group.objects.get(name='Administrador')
    if not user.groups.filter(name='Administrador').exists():
        user.groups.add(admin_group)
        print("Superuser already exists - added to 'Administrador' group")
    else:
        print("Superuser already exists and is in 'Administrador' group")
EOF
echo " "




