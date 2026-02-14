# Generated migration - Vendas de exemplo para visualização

from decimal import Decimal
from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def criar_vendas_exemplo(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    Cliente = apps.get_model('clientes', 'Cliente')
    Produto = apps.get_model('produtos', 'Produto')
    FormaPagamento = apps.get_model('promocoes', 'FormaPagamento')
    Venda = apps.get_model('vendas', 'Venda')
    ItemVenda = apps.get_model('vendas', 'ItemVenda')
    User = apps.get_model('usuarios', 'Usuario')

    for empresa in Empresa.objects.all():
        if Venda.objects.filter(empresa=empresa).exists():
            continue

        produtos = list(Produto.objects.filter(empresa=empresa, ativo=True)[:5])
        clientes = list(Cliente.objects.filter(empresa=empresa)[:3])
        formas = list(FormaPagamento.objects.filter(empresa=empresa, ativo=True))
        vendedor = User.objects.filter(empresa=empresa).first()

        if not produtos:
            continue

        formas = formas[:4] if len(formas) >= 4 else formas
        forma_nomes = ['PIX', 'Dinheiro', 'Cartão Crédito', 'Cartão Débito'][:len(formas)]
        if formas:
            formas_dict = {f.nome: f for f in formas}
        else:
            formas_dict = {}

        # Criar vendas de exemplo nos últimos dias
        def itens_para_venda(n):
            idxs = [i % len(produtos) for i in range(min(3, len(produtos)))]
            return [(idx, (n + idx) % 3 + 1) for idx in idxs]

        hoje = timezone.now().date()
        for i in range(9):
            data_venda = hoje - timedelta(days=i % 7)
            dt = timezone.make_aware(
                timezone.datetime(data_venda.year, data_venda.month, data_venda.day, 10 + i % 8, 30)
            )
            cliente = clientes[i % len(clientes)] if clientes else None
            forma_nome = forma_nomes[i % len(forma_nomes)]
            forma = formas_dict.get(forma_nome) if formas_dict else None
            itens = itens_para_venda(i)

            ultima = Venda.objects.filter(empresa=empresa).order_by('-numero').first()
            proximo_numero = (ultima.numero + 1) if ultima else 1

            venda = Venda.objects.create(
                empresa=empresa,
                cliente=cliente,
                vendedor=vendedor,
                forma_pagamento=forma,
                numero=proximo_numero,
                desconto_total=Decimal('0'),
                taxa_pagamento=Decimal('0'),
                total=Decimal('0'),
                criado_em=dt,
            )

            total = Decimal('0')
            for idx_prod, qtd in itens:
                if idx_prod >= len(produtos):
                    continue
                prod = produtos[idx_prod]
                preco = prod.preco_venda
                subtotal = preco * qtd
                ItemVenda.objects.create(
                    venda=venda,
                    produto=prod,
                    quantidade=qtd,
                    preco_unitario=preco,
                    desconto=Decimal('0'),
                    subtotal=subtotal,
                )
                total += subtotal
                prod.estoque_atual -= qtd
                prod.save(update_fields=['estoque_atual'])

            venda.total = total
            venda.save(update_fields=['total'])


def remover_vendas_exemplo(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_clientes_exemplo'),
        ('produtos', '0002_produtos_exemplo'),
        ('promocoes', '0002_formas_exemplo'),
        ('vendas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_vendas_exemplo, remover_vendas_exemplo),
    ]
