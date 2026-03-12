"""
PDV, listas de pedido, resumo antes do checkout e dashboard.
"""
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import json

from apps.produtos.models import Produto, Categoria
from apps.clientes.models import Cliente
from apps.promocoes.models import FormaPagamento, RegraDesconto
from .models import ListaPedido, ItemListaPedido, Venda, ItemVenda


def _empresa_usuario(request):
    return getattr(request.user, 'empresa', None)


@login_required
def pdv(request):
    """Ponto de venda: carrinho em sessão ou lista de pedido."""
    empresa = _empresa_usuario(request)
    if not empresa:
        messages.error(request, 'Usuário sem empresa vinculada.')
        return redirect('logout')
    lista_id = request.session.get('lista_pedido_id')
    lista = None
    if lista_id:
        lista = ListaPedido.objects.filter(
            pk=lista_id, empresa=empresa, finalizada=False
        ).first()
    produtos = Produto.objects.filter(empresa=empresa, ativo=True).order_by('nome')
    formas_pagamento = FormaPagamento.objects.filter(empresa=empresa, ativo=True)
    produtos_vencidos = Produto.objects.filter(
        empresa=empresa, ativo=True, data_validade__lt=timezone.localdate()
    )[:20]
    produtos_proximo_vencimento = Produto.objects.filter(
        empresa=empresa, ativo=True, data_validade__gte=timezone.localdate(),
        data_validade__lte=timezone.localdate() + timedelta(days=30)
    )[:20]
    subtotal = sum(i.subtotal for i in lista.itens.all()) if lista and lista.itens.exists() else Decimal('0')
    context = {
        'lista': lista,
        'subtotal': subtotal,
        'produtos': produtos,
        'formas_pagamento': formas_pagamento,
        'produtos_vencidos': produtos_vencidos,
        'produtos_proximo_vencimento': produtos_proximo_vencimento,
    }
    return render(request, 'vendas/pdv.html', context)


@login_required
def lista_pedido_criar(request):
    """Cria uma nova lista de pedido e guarda na sessão."""
    empresa = _empresa_usuario(request)
    if not empresa:
        return redirect('logout')
    lista = ListaPedido.objects.create(
        empresa=empresa,
        vendedor=request.user,
        nome=f'Pedido {timezone.now().strftime("%d/%m/%Y %H:%M")}'
    )
    request.session['lista_pedido_id'] = lista.pk
    return redirect('vendas:pdv')


@login_required
def item_adicionar(request):
    """Adiciona produto ao carrinho (lista de pedido) via POST."""
    empresa = _empresa_usuario(request)
    if not empresa:
        return JsonResponse({'ok': False, 'erro': 'Sem empresa'}, status=400)
    lista_id = request.session.get('lista_pedido_id')
    if not lista_id:
        lista = ListaPedido.objects.create(
            empresa=empresa, vendedor=request.user,
            nome=f'Pedido {timezone.now().strftime("%d/%m/%Y %H:%M")}'
        )
        request.session['lista_pedido_id'] = lista.pk
    else:
        lista = get_object_or_404(ListaPedido, pk=lista_id, empresa=empresa, finalizada=False)
    produto_id = request.POST.get('produto_id')
    quantidade = Decimal(request.POST.get('quantidade', '1').replace(',', '.'))
    if not produto_id or quantidade <= 0:
        return JsonResponse({'ok': False, 'erro': 'Dados inválidos'}, status=400)
    produto = get_object_or_404(Produto, pk=produto_id, empresa=empresa, ativo=True)
    item, created = ItemListaPedido.objects.get_or_create(
        lista=lista, produto=produto,
        defaults={'quantidade': quantidade, 'preco_unitario': produto.preco_venda}
    )
    if not created:
        item.quantidade += quantidade
        item.save()
    return JsonResponse({'ok': True, 'itens_count': lista.itens.count()})


@login_required
def item_remover(request, item_id):
    """Remove item da lista."""
    empresa = _empresa_usuario(request)
    item = get_object_or_404(ItemListaPedido, pk=item_id, lista__empresa=empresa)
    item.delete()
    return redirect('vendas:pdv')


@login_required
def item_alterar_qtd(request, item_id):
    """Altera quantidade do item (POST: quantidade)."""
    empresa = _empresa_usuario(request)
    item = get_object_or_404(ItemListaPedido, pk=item_id, lista__empresa=empresa)
    qtd = request.POST.get('quantidade')
    try:
        qtd = Decimal(qtd.replace(',', '.'))
        if qtd <= 0:
            item.delete()
        else:
            item.quantidade = qtd
            item.save()
    except (ValueError, TypeError):
        pass
    return redirect('vendas:pdv')


@login_required
def resumo_checkout(request):
    """Tela de resumo com todos os produtos antes de finalizar a compra."""
    empresa = _empresa_usuario(request)
    lista_id = request.session.get('lista_pedido_id')
    if not lista_id:
        messages.info(request, 'Nenhum pedido em andamento.')
        return redirect('vendas:pdv')
    lista = get_object_or_404(ListaPedido, pk=lista_id, empresa=empresa, finalizada=False)
    if not lista.itens.exists():
        messages.warning(request, 'Adicione itens ao pedido.')
        return redirect('vendas:pdv')
    formas_pagamento = FormaPagamento.objects.filter(empresa=empresa, ativo=True)
    subtotal = sum(i.subtotal for i in lista.itens.all())
    context = {
        'lista': lista,
        'subtotal': subtotal,
        'formas_pagamento': formas_pagamento,
    }
    return render(request, 'vendas/resumo_checkout.html', context)


@login_required
def finalizar_venda(request):
    """Finaliza a venda: cria Venda, ItemVenda, baixa estoque e limpa sessão."""
    empresa = _empresa_usuario(request)
    lista_id = request.session.get('lista_pedido_id')
    if not lista_id:
        messages.error(request, 'Nenhum pedido em andamento.')
        return redirect('vendas:pdv')
    lista = get_object_or_404(ListaPedido, pk=lista_id, empresa=empresa, finalizada=False)
    if not lista.itens.exists():
        messages.warning(request, 'Adicione itens ao pedido.')
        return redirect('vendas:pdv')
    forma_id = request.POST.get('forma_pagamento')
    desconto_total = Decimal(request.POST.get('desconto_total', '0').replace(',', '.'))
    cliente_id = request.POST.get('cliente_id') or None
    forma = None
    if forma_id:
        forma = FormaPagamento.objects.filter(pk=forma_id, empresa=empresa).first()
    subtotal = sum(i.subtotal for i in lista.itens.all())
    total_itens = subtotal - desconto_total
    taxa = Decimal('0')
    if forma:
        taxa = forma.calcular_taxa(total_itens)
    total_final = total_itens + taxa
    venda = Venda.objects.create(
        empresa=empresa,
        cliente_id=cliente_id or lista.cliente_id,
        vendedor=request.user,
        desconto_total=desconto_total,
        taxa_pagamento=taxa,
        total=total_final,
        forma_pagamento=forma,
    )
    for item in lista.itens.all():
        ItemVenda.objects.create(
            venda=venda,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            desconto=item.desconto,
            subtotal=item.subtotal,
        )
        item.produto.estoque_atual -= item.quantidade
        item.produto.save(update_fields=['estoque_atual'])
    lista.finalizada = True
    lista.save()
    if 'lista_pedido_id' in request.session:
        del request.session['lista_pedido_id']
    messages.success(request, f'Venda #{venda.numero} finalizada. Total: R$ {venda.total:.2f}')
    return redirect('vendas:pdv')


@login_required
def aplicar_desconto_item(request, item_id):
    """Aplica desconto em um item da lista (POST: valor)."""
    empresa = _empresa_usuario(request)
    item = get_object_or_404(ItemListaPedido, pk=item_id, lista__empresa=empresa)
    try:
        valor = Decimal(request.POST.get('desconto', '0').replace(',', '.'))
        item.desconto = max(Decimal('0'), min(valor, item.quantidade * item.preco_unitario))
        item.save()
    except (ValueError, TypeError):
        pass
    return redirect('vendas:resumo_checkout')


def _parse_date(s):
    """Parse YYYY-MM-DD string to date or None."""
    if not s or not isinstance(s, str):
        return None
    try:
        from datetime import datetime
        return datetime.strptime(s.strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


@login_required
def dashboard(request):
    """Dashboard para Gestor: vendas mensais e análise."""
    if not request.user.is_gestor:
        messages.error(request, 'Acesso restrito ao gestor.')
        return redirect('vendas:pdv')
    empresa = _empresa_usuario(request)
    if not empresa:
        return redirect('logout')
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)

    # Filtro de período (calendário)
    data_inicio = _parse_date(request.GET.get('data_inicio'))
    data_fim = _parse_date(request.GET.get('data_fim'))
    if data_inicio and data_fim and data_inicio > data_fim:
        data_inicio, data_fim = data_fim, data_inicio
    if not data_inicio:
        data_inicio = inicio_mes
    if not data_fim:
        data_fim = hoje
    filtro_periodo = bool(request.GET.get('data_inicio') or request.GET.get('data_fim'))

    vendas_mes = Venda.objects.filter(
        empresa=empresa,
        criado_em__date__gte=data_inicio,
        criado_em__date__lte=data_fim
    )
    total_mes = vendas_mes.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    quantidade_mes = vendas_mes.count()
    vendas_hoje = Venda.objects.filter(empresa=empresa, criado_em__date=hoje)
    total_hoje = vendas_hoje.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    ultimas_vendas = Venda.objects.filter(
        empresa=empresa,
        criado_em__date__gte=data_inicio,
        criado_em__date__lte=data_fim
    ).order_by('-criado_em')[:15]

    # Dados para gráfico 1: vendas por dia no período
    vendas_por_dia = (
        Venda.objects.filter(
            empresa=empresa,
            criado_em__date__gte=data_inicio,
            criado_em__date__lte=data_fim,
        )
        .annotate(data=TruncDate('criado_em'))
        .values('data')
        .annotate(total=Sum('total'))
        .order_by('data')
    )
    chart_vendas_dia_labels = [v['data'].strftime('%d/%m') for v in vendas_por_dia]
    chart_vendas_dia_valores = [float(v['total']) for v in vendas_por_dia]

    # Dados para gráfico 2: vendas por forma de pagamento
    vendas_por_forma = (
        Venda.objects.filter(
            empresa=empresa,
            criado_em__date__gte=data_inicio,
            criado_em__date__lte=data_fim,
        )
        .values('forma_pagamento__nome')
        .annotate(total=Sum('total'))
        .order_by('-total')
    )
    chart_formas_labels = []
    chart_formas_valores = []
    for v in vendas_por_forma:
        nome = v['forma_pagamento__nome'] or 'Não informado'
        chart_formas_labels.append(nome)
        chart_formas_valores.append(float(v['total']))

    # Dados para visualização de estoque
    produtos_ativos = Produto.objects.filter(empresa=empresa, ativo=True)
    estoque_zerado = produtos_ativos.filter(estoque_atual=0).count()
    estoque_baixo = produtos_ativos.filter(estoque_atual__gt=0, estoque_atual__lt=5).count()
    estoque_ok = produtos_ativos.filter(estoque_atual__gte=5).count()
    chart_estoque_labels = ['OK (≥5)', 'Baixo (<5)', 'Zerado']
    chart_estoque_valores = [estoque_ok, estoque_baixo, estoque_zerado]

    # Estoque por categoria
    estoque_por_cat = (
        Produto.objects.filter(empresa=empresa, ativo=True, categoria__isnull=False)
        .values('categoria__nome')
        .annotate(total=Sum('estoque_atual'))
        .order_by('-total')[:8]
    )
    chart_estoque_cat_labels = [v['categoria__nome'] for v in estoque_por_cat]
    chart_estoque_cat_valores = [float(v['total']) for v in estoque_por_cat]

    context = {
        'total_mes': total_mes,
        'quantidade_mes': quantidade_mes,
        'total_hoje': total_hoje,
        'vendas_hoje_count': vendas_hoje.count(),
        'ultimas_vendas': ultimas_vendas,
        'inicio_mes': inicio_mes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'filtro_periodo': filtro_periodo,
        'chart_vendas_dia_labels': json.dumps(chart_vendas_dia_labels),
        'chart_vendas_dia_valores': json.dumps(chart_vendas_dia_valores),
        'chart_formas_labels': json.dumps(chart_formas_labels),
        'chart_formas_valores': json.dumps(chart_formas_valores),
        'chart_vendas_dia_tem_dados': bool(chart_vendas_dia_labels),
        'chart_formas_tem_dados': bool(chart_formas_labels),
        'chart_formas_count': len(chart_formas_labels),
        'estoque_total_produtos': produtos_ativos.count(),
        'estoque_zerado': estoque_zerado,
        'estoque_baixo': estoque_baixo,
        'estoque_ok': estoque_ok,
        'chart_estoque_labels': json.dumps(chart_estoque_labels),
        'chart_estoque_valores': json.dumps(chart_estoque_valores),
        'chart_estoque_cat_labels': json.dumps(chart_estoque_cat_labels),
        'chart_estoque_cat_valores': json.dumps(chart_estoque_cat_valores),
    }
    return render(request, 'vendas/dashboard.html', context)


@login_required
def vendas_lista(request):
    """Listagem de vendas (Gestor vê todas; atendente não tem acesso ou vê só as suas)."""
    empresa = _empresa_usuario(request)
    if not empresa:
        return redirect('logout')
    vendas = Venda.objects.filter(empresa=empresa).order_by('-criado_em')
    if request.user.is_atendente:
        vendas = vendas.filter(vendedor=request.user)
    vendas = vendas[:100]
    return render(request, 'vendas/lista_vendas.html', {'vendas': vendas})


@login_required
def buscar_codigo_barras(request):
    """API: busca produto por código de barras (GET ?codigo=)."""
    empresa = _empresa_usuario(request)
    codigo = (request.GET.get('codigo') or '').strip()
    if not codigo:
        return JsonResponse({'ok': False}, status=400)
    produto = Produto.objects.filter(
        empresa=empresa, codigo_barras=codigo, ativo=True
    ).first()
    if not produto:
        return JsonResponse({'ok': False, 'erro': 'Produto não encontrado'})
    return JsonResponse({
        'ok': True,
        'id': produto.pk,
        'nome': produto.nome,
        'preco': str(produto.preco_venda),
        'estoque': str(produto.estoque_atual),
        'vencido': produto.esta_vencido(),
    })
