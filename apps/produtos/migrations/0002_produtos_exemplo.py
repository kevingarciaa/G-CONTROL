# Generated migration - Produtos e categorias de exemplo com estoque

from decimal import Decimal
from django.db import migrations


def criar_produtos_exemplo(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    Categoria = apps.get_model('produtos', 'Categoria')
    Produto = apps.get_model('produtos', 'Produto')

    categorias_produtos = [
        ('Bebidas', [
            {'nome': 'Refrigerante Cola 2L', 'codigo_barras': '7891234567890', 'preco_venda': Decimal('8.90'), 'preco_custo': Decimal('4.50'), 'estoque_atual': 48, 'unidade': 'UN'},
            {'nome': 'Água Mineral 500ml', 'codigo_barras': '7891234567891', 'preco_venda': Decimal('2.50'), 'preco_custo': Decimal('0.80'), 'estoque_atual': 120, 'unidade': 'UN'},
            {'nome': 'Suco Laranja 1L', 'codigo_barras': '7891234567892', 'preco_venda': Decimal('6.90'), 'preco_custo': Decimal('3.20'), 'estoque_atual': 36, 'unidade': 'UN'},
        ]),
        ('Alimentos', [
            {'nome': 'Arroz 5kg', 'codigo_barras': '7891234567893', 'preco_venda': Decimal('22.90'), 'preco_custo': Decimal('14.00'), 'estoque_atual': 80, 'unidade': 'UN'},
            {'nome': 'Feijão 1kg', 'codigo_barras': '7891234567894', 'preco_venda': Decimal('7.50'), 'preco_custo': Decimal('4.20'), 'estoque_atual': 150, 'unidade': 'UN'},
            {'nome': 'Óleo 900ml', 'codigo_barras': '7891234567895', 'preco_venda': Decimal('9.90'), 'preco_custo': Decimal('5.50'), 'estoque_atual': 60, 'unidade': 'UN'},
        ]),
        ('Limpeza', [
            {'nome': 'Sabão em Pó 1kg', 'codigo_barras': '7891234567896', 'preco_venda': Decimal('12.90'), 'preco_custo': Decimal('7.00'), 'estoque_atual': 45, 'unidade': 'UN'},
            {'nome': 'Detergente 500ml', 'codigo_barras': '7891234567897', 'preco_venda': Decimal('3.50'), 'preco_custo': Decimal('1.80'), 'estoque_atual': 90, 'unidade': 'UN'},
        ]),
    ]

    for empresa in Empresa.objects.all():
        if not Produto.objects.filter(empresa=empresa).exists():
            for cat_nome, produtos in categorias_produtos:
                cat, _ = Categoria.objects.get_or_create(empresa=empresa, nome=cat_nome)
                for p in produtos:
                    Produto.objects.create(empresa=empresa, categoria=cat, **p)


def remover_produtos_exemplo(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_produtos_exemplo, remover_produtos_exemplo),
    ]
