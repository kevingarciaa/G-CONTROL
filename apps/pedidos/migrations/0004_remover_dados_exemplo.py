# Remove dados mocados (setores e pedidos de exemplo)

from django.db import migrations


def remover_dados_exemplo(apps, schema_editor):
    Setor = apps.get_model('pedidos', 'Setor')
    Pedido = apps.get_model('pedidos', 'Pedido')

    # Desvincula pedidos dos setores antes de apagar os setores
    Pedido.objects.filter(setor_atual__isnull=False).update(setor_atual=None)
    # Remove todos os pedidos
    Pedido.objects.all().delete()
    # Remove os setores de exemplo (criados pela migração 0002)
    Setor.objects.filter(
        nome__in=['Corte', 'Costura', 'Acabamento', 'Expedição']
    ).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0003_metas_valor'),
    ]

    operations = [
        migrations.RunPython(remover_dados_exemplo, noop),
    ]
