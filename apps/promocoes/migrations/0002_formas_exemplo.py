# Generated migration - Formas de pagamento de exemplo

from django.db import migrations


def criar_formas_exemplo(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    FormaPagamento = apps.get_model('promocoes', 'FormaPagamento')

    formas = [
        {'nome': 'Dinheiro', 'taxa_percentual': 0},
        {'nome': 'PIX', 'taxa_percentual': 0},
        {'nome': 'Cartão Débito', 'taxa_percentual': 1.5},
        {'nome': 'Cartão Crédito', 'taxa_percentual': 3.0},
    ]

    for empresa in Empresa.objects.all():
        if not FormaPagamento.objects.filter(empresa=empresa).exists():
            for f in formas:
                FormaPagamento.objects.create(empresa=empresa, **f)


def remover_formas_exemplo(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('promocoes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_formas_exemplo, remover_formas_exemplo),
    ]
