# Generated migration - Substitui produtos de exemplo por tecidos

from decimal import Decimal
from django.db import migrations


def trocar_por_tecidos(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    Categoria = apps.get_model('produtos', 'Categoria')
    Produto = apps.get_model('produtos', 'Produto')

    categorias_produtos = [
        ('Tecidos por Metro', [
            {'nome': 'Tecido em Metro Algodão Cru', 'codigo_barras': '7891234567890', 'preco_venda': Decimal('12.90'), 'preco_custo': Decimal('6.50'), 'estoque_atual': 48, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Algodão Azul', 'codigo_barras': '7891234567891', 'preco_venda': Decimal('13.50'), 'preco_custo': Decimal('6.80'), 'estoque_atual': 35, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Algodão Branco', 'codigo_barras': '7891234567892', 'preco_venda': Decimal('12.90'), 'preco_custo': Decimal('6.50'), 'estoque_atual': 52, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Malha Preta', 'codigo_barras': '7891234567893', 'preco_venda': Decimal('15.90'), 'preco_custo': Decimal('8.00'), 'estoque_atual': 40, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Malha Vermelha', 'codigo_barras': '7891234567894', 'preco_venda': Decimal('15.90'), 'preco_custo': Decimal('8.00'), 'estoque_atual': 28, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Linho Natural', 'codigo_barras': '7891234567895', 'preco_venda': Decimal('24.90'), 'preco_custo': Decimal('12.50'), 'estoque_atual': 22, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Sarja Bege', 'codigo_barras': '7891234567896', 'preco_venda': Decimal('18.90'), 'preco_custo': Decimal('9.50'), 'estoque_atual': 30, 'unidade': 'M'},
            {'nome': 'Tecido em Metro Cetim Rosa', 'codigo_barras': '7891234567897', 'preco_venda': Decimal('16.50'), 'preco_custo': Decimal('8.20'), 'estoque_atual': 25, 'unidade': 'M'},
        ]),
        ('Rolos', [
            {'nome': 'Rolo Com 10 Metros Algodão Cru', 'codigo_barras': '7891234567898', 'preco_venda': Decimal('115.00'), 'preco_custo': Decimal('58.00'), 'estoque_atual': 18, 'unidade': 'UN'},
            {'nome': 'Rolo Com 10 Metros Linho Natural', 'codigo_barras': '7891234567899', 'preco_venda': Decimal('220.00'), 'preco_custo': Decimal('110.00'), 'estoque_atual': 12, 'unidade': 'UN'},
            {'nome': 'Rolo Com 10 Metros Malha Preta', 'codigo_barras': '7891234567900', 'preco_venda': Decimal('140.00'), 'preco_custo': Decimal('70.00'), 'estoque_atual': 15, 'unidade': 'UN'},
            {'nome': 'Rolo Com 10 Metros Sarja Bege', 'codigo_barras': '7891234567901', 'preco_venda': Decimal('165.00'), 'preco_custo': Decimal('82.50'), 'estoque_atual': 10, 'unidade': 'UN'},
        ]),
    ]

    for empresa in Empresa.objects.all():
        for cat_nome, produtos in categorias_produtos:
            cat, _ = Categoria.objects.get_or_create(empresa=empresa, nome=cat_nome)
            for p in produtos:
                Produto.objects.get_or_create(
                    empresa=empresa,
                    codigo_barras=p['codigo_barras'],
                    defaults={'nome': p['nome'], 'categoria': cat, 'preco_venda': p['preco_venda'],
                              'preco_custo': p['preco_custo'], 'estoque_atual': p['estoque_atual'], 'unidade': p['unidade']}
                )


def reverter_tecidos(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0002_produtos_exemplo'),
    ]

    operations = [
        migrations.RunPython(trocar_por_tecidos, reverter_tecidos),
    ]
