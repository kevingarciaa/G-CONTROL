# Generated migration - Renomeia produtos de alimentos para tecidos

from decimal import Decimal
from django.db import migrations


# Mapeamento: nome antigo -> (nome novo, preco_venda, preco_custo, unidade)
RENOMEAR = {
    'Refrigerante Cola 2L': ('Tecido em Metro Algodão Cru', Decimal('12.90'), Decimal('6.50'), 'M'),
    'Água Mineral 500ml': ('Tecido em Metro Algodão Azul', Decimal('13.50'), Decimal('6.80'), 'M'),
    'Suco Laranja 1L': ('Tecido em Metro Algodão Branco', Decimal('12.90'), Decimal('6.50'), 'M'),
    'Arroz 5kg': ('Tecido em Metro Malha Preta', Decimal('15.90'), Decimal('8.00'), 'M'),
    'Feijão 1kg': ('Tecido em Metro Malha Vermelha', Decimal('15.90'), Decimal('8.00'), 'M'),
    'Óleo 900ml': ('Tecido em Metro Linho Natural', Decimal('24.90'), Decimal('12.50'), 'M'),
    'Sabão em Pó 1kg': ('Tecido em Metro Sarja Bege', Decimal('18.90'), Decimal('9.50'), 'M'),
    'Detergente 500ml': ('Tecido em Metro Cetim Rosa', Decimal('16.50'), Decimal('8.20'), 'M'),
}


def renomear_alimentos_tecidos(apps, schema_editor):
    Categoria = apps.get_model('produtos', 'Categoria')
    Produto = apps.get_model('produtos', 'Produto')

    for nome_antigo, (nome_novo, preco_venda, preco_custo, unidade) in RENOMEAR.items():
        produtos = Produto.objects.filter(nome=nome_antigo)
        for produto in produtos:
            cat_tecidos = Categoria.objects.filter(empresa=produto.empresa, nome='Tecidos por Metro').first()
            if not cat_tecidos:
                cat_tecidos = Categoria.objects.create(empresa=produto.empresa, nome='Tecidos por Metro')
            produto.nome = nome_novo
            produto.preco_venda = preco_venda
            produto.preco_custo = preco_custo
            produto.unidade = unidade
            produto.categoria = cat_tecidos
            produto.save()

    # Remover categorias vazias (Bebidas, Alimentos, Limpeza)
    for cat_nome in ['Bebidas', 'Alimentos', 'Limpeza']:
        for cat in Categoria.objects.filter(nome=cat_nome):
            if not Produto.objects.filter(categoria=cat).exists():
                cat.delete()


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0003_tecidos_exemplo'),
    ]

    operations = [
        migrations.RunPython(renomear_alimentos_tecidos, reverter),
    ]
