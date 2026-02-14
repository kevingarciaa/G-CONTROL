# Migração de dados de exemplo desativada (dados mocados removidos)

from django.db import migrations


def criar_setores_exemplo(apps, schema_editor):
    pass  # Dados mocados removidos – não insere mais exemplos


def criar_pedidos_exemplo(apps, schema_editor):
    pass  # Dados mocados removidos – não insere mais exemplos


def remover_pedidos_exemplo(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_setores_exemplo, migrations.RunPython.noop),
        migrations.RunPython(criar_pedidos_exemplo, remover_pedidos_exemplo),
    ]
