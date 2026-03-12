# Generated migration - seed usuário gustavo_vieira

import os
from django.db import migrations


def create_gustavo_vieira(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    Empresa = apps.get_model('empresas', 'Empresa')

    if Usuario.objects.filter(username='gustavo_vieira').exists():
        return

    # Cria empresa padrão se não existir (necessária para o usuário)
    empresa = Empresa.objects.first()
    if not empresa:
        empresa = Empresa.objects.create(
            nome='GControl',
            nome_fantasia='GControl',
        )

    # Senha via variável de ambiente ou padrão (definir GUSTAVO_VIEIRA_PASSWORD no Render)
    senha = os.environ.get('GUSTAVO_VIEIRA_PASSWORD', 'GControl2026!')

    Usuario.objects.create_user(
        username='gustavo_vieira',
        password=senha,
        first_name='Gustavo',
        last_name='Vieira',
        email='gustavo_vieira@example.com',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        tipo='GESTOR',
        empresa=empresa,
    )


def reverse_create_gustavo_vieira(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.filter(username='gustavo_vieira').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_gustavo_vieira, reverse_create_gustavo_vieira),
    ]
