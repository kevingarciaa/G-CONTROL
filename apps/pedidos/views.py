from decimal import Decimal
from datetime import timedelta, date

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.conf import settings
from django.utils import timezone as tz

from .models import Setor, Pedido, ItemPedido, MetaValor, STATUS_PEDIDO
from .forms import SetorForm, PedidoForm, MetasValorForm, TAMANHOS_POR_CATEGORIA


def _empresa(request):
    return getattr(request.user, 'empresa', None)


def _easter(year):
    """Data da Páscoa (algoritmo de Meeus)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _feriados_brasil(year):
    """Feriados nacionais do Brasil no ano (datas como date)."""
    pascoa = _easter(year)
    sexta_santa = pascoa - timedelta(days=2)
    return [
        (date(year, 1, 1), 'Ano Novo'),
        (date(year, 4, 21), 'Tiradentes'),
        (date(year, 5, 1), 'Dia do Trabalho'),
        (sexta_santa, 'Sexta-feira Santa'),
        (date(year, 9, 7), 'Independência do Brasil'),
        (date(year, 10, 12), 'N. Sra. Aparecida'),
        (date(year, 11, 2), 'Finados'),
        (date(year, 11, 15), 'Proclamação da República'),
        (date(year, 12, 25), 'Natal'),
    ]


def _calendario_resumo(data_inicio, data_fim):
    """
    Entre data_inicio e data_fim (inclusive), retorna:
    total_dias, dias_uteis, fins_de_semana, feriados, lista_feriados.
    """
    feriados_set = set()
    feriados_com_nome = []  # (data, nome) no período
    for y in range(data_inicio.year, data_fim.year + 1):
        for d, nome in _feriados_brasil(y):
            feriados_set.add(d)
            if data_inicio <= d <= data_fim:
                feriados_com_nome.append((d, nome))
    feriados_com_nome.sort(key=lambda x: x[0])
    total_dias = (data_fim - data_inicio).days + 1
    fins_de_semana = 0
    feriados_no_periodo = 0
    dias_uteis = 0
    d = data_inicio
    while d <= data_fim:
        w = d.weekday()  # 0=seg, 6=dom
        is_weekend = w >= 5
        is_holiday = d in feriados_set
        if is_weekend:
            fins_de_semana += 1
        if is_holiday:
            feriados_no_periodo += 1
        if not is_weekend and not is_holiday:
            dias_uteis += 1
        d += timedelta(days=1)
    return {
        'total_dias': total_dias,
        'dias_uteis': dias_uteis,
        'fins_de_semana': fins_de_semana,
        'feriados': feriados_no_periodo,
        'lista_feriados': feriados_com_nome,
    }


def _dias_alerta_setor():
    return getattr(settings, 'PEDIDOS_ALERTA_SETOR_DIAS', 3)


SESSION_RASCUNHO_ITENS = 'pedido_rascunho_itens'
SESSION_RASCUNHO_HEADER = 'pedido_rascunho_header'


def _itens_rascunho(request):
    """Lista de itens do rascunho (novo pedido) na sessão."""
    return request.session.get(SESSION_RASCUNHO_ITENS, [])


def _totais_rascunho(itens):
    """Retorna (total_receber, total_custo) a partir da lista de itens da sessão."""
    total_r = Decimal('0')
    total_c = Decimal('0')
    for i in itens:
        qtd = Decimal(str(i['quantidade']))
        total_r += qtd * Decimal(str(i['preco_unitario']))
        total_c += qtd * Decimal(str(i['preco_custo_unitario']))
    return total_r.quantize(Decimal('0.01')), total_c.quantize(Decimal('0.01'))


@login_required
def dashboard(request):
    """Dashboard: pedidos em produção, atraso, totais, lucro e alertas de setor. Filtro por pedido."""
    from django.utils import timezone

    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')

    hoje = timezone.localdate()
    fim_do_ano = date(hoje.year, 12, 31)
    dias_ate_fim_do_ano = (fim_do_ano - hoje).days
    if dias_ate_fim_do_ano < 0:
        fim_do_ano = date(hoje.year + 1, 12, 31)
        dias_ate_fim_do_ano = (fim_do_ano - hoje).days
    calendario = _calendario_resumo(hoje, fim_do_ano)
    pedido_id = request.GET.get('pedido_id')
    pedidos_para_filtro = Pedido.objects.filter(empresa=empresa).exclude(
        status='CANCELADO'
    ).select_related('cliente').order_by('-numero')[:300]
    pedido_selecionado = None

    if pedido_id:
        pedido_selecionado = get_object_or_404(
            Pedido.objects.select_related('cliente', 'setor_atual'),
            pk=pedido_id, empresa=empresa
        )
        # Visão por um único pedido
        em_producao = [pedido_selecionado] if pedido_selecionado.status == 'EM_PRODUCAO' else []
        em_atraso = (
            [pedido_selecionado]
            if pedido_selecionado.status == 'EM_PRODUCAO' and pedido_selecionado.em_atraso
            else []
        )
        em_producao_count = 1 if pedido_selecionado.status == 'EM_PRODUCAO' else 0
        em_atraso_count = 1 if (pedido_selecionado.status == 'EM_PRODUCAO' and pedido_selecionado.em_atraso) else 0
        total_a_receber = Decimal('0') if pedido_selecionado.recebido else pedido_selecionado.valor_total
        total_a_pagar = Decimal('0') if pedido_selecionado.pago else pedido_selecionado.valor_custo
        lucro = pedido_selecionado.valor_total - pedido_selecionado.valor_custo
        total_pecas_produzidas = pedido_selecionado.itens.aggregate(s=Sum('quantidade'))['s'] or Decimal('0')
        # Alertas: só este pedido se estiver parado
        dias_alerta = _dias_alerta_setor()
        alertas_por_setor = {}
        if (
            pedido_selecionado.setor_atual_id
            and pedido_selecionado.data_entrada_setor
        ):
            dias = pedido_selecionado.dias_no_setor_atual()
            if dias is not None and dias >= dias_alerta:
                alertas_por_setor[pedido_selecionado.setor_atual.nome] = [
                    (pedido_selecionado, dias)
                ]
    else:
        # Visão geral
        em_producao = Pedido.objects.filter(
            empresa=empresa, status='EM_PRODUCAO'
        ).select_related('cliente', 'setor_atual').order_by(
            'data_prevista_entrega', 'numero'
        )[:20]
        # Em atraso: atraso por setor (EM_PRODUCAO + previsão setor vencida) OU atraso pedido completo (previsão pedido completo vencida, não entregue)
        q_atraso = (
            Q(status='EM_PRODUCAO', data_prevista_entrega__lt=hoje)
            | (Q(data_prevista_entrega_completo__lt=hoje, data_prevista_entrega_completo__isnull=False) & ~Q(status='ENTREGUE'))
        )
        em_atraso = Pedido.objects.filter(empresa=empresa).filter(
            q_atraso
        ).exclude(status='CANCELADO').distinct().select_related(
            'cliente', 'setor_atual'
        ).order_by('data_prevista_entrega', 'data_prevista_entrega_completo', 'numero')[:20]
        em_producao_count = Pedido.objects.filter(empresa=empresa, status='EM_PRODUCAO').count()
        em_atraso_count = Pedido.objects.filter(empresa=empresa).filter(
            q_atraso
        ).exclude(status='CANCELADO').distinct().count()

        ativos = Pedido.objects.filter(empresa=empresa).exclude(status='CANCELADO')
        total_a_receber = ativos.filter(recebido=False).aggregate(
            s=Sum('valor_total')
        )['s'] or Decimal('0')
        total_a_pagar = ativos.filter(pago=False).aggregate(
            s=Sum('valor_custo')
        )['s'] or Decimal('0')
        # Lucro realizado = soma (valor_total - valor_custo) de todos os pedidos não cancelados
        lucro = Pedido.objects.filter(empresa=empresa).exclude(
            status='CANCELADO'
        ).aggregate(
            total=Sum(F('valor_total') - F('valor_custo'))
        )['total']
        if lucro is None:
            lucro = Decimal('0')
        else:
            lucro = Decimal(str(lucro)).quantize(Decimal('0.01'))
        total_pecas_produzidas = ItemPedido.objects.filter(
            pedido__empresa=empresa
        ).exclude(pedido__status='CANCELADO').aggregate(s=Sum('quantidade'))['s'] or Decimal('0')

        dias_alerta = _dias_alerta_setor()
        pedidos_parados = []
        for p in Pedido.objects.filter(
            empresa=empresa,
            status='EM_PRODUCAO',
            setor_atual__isnull=False,
            data_entrada_setor__isnull=False
        ).select_related('cliente', 'setor_atual'):
            dias = p.dias_no_setor_atual()
            if dias is not None and dias >= dias_alerta:
                pedidos_parados.append((p, dias))
        alertas_por_setor = {}
        for p, dias in pedidos_parados:
            nome_setor = p.setor_atual.nome
            if nome_setor not in alertas_por_setor:
                alertas_por_setor[nome_setor] = []
            alertas_por_setor[nome_setor].append((p, dias))

    # Metas de valor (para exibição de progresso); com período editável
    meta_receber = MetaValor.objects.filter(empresa=empresa, tipo='RECEBER').first()
    meta_lucro = MetaValor.objects.filter(empresa=empresa, tipo='LUCRO').first()
    meta_producao = MetaValor.objects.filter(empresa=empresa, tipo='PRODUCAO').first()

    total_para_meta_receber = total_a_receber
    total_para_meta_lucro = lucro
    total_para_meta_producao = total_pecas_produzidas
    if not pedido_selecionado:
        if meta_producao and meta_producao.periodo_dias:
            data_inicio_p = hoje - timedelta(days=meta_producao.periodo_dias)
            total_para_meta_producao = _total_pecas_periodo(empresa, data_inicio_p, hoje)
        if meta_receber and meta_receber.periodo_dias:
            data_inicio_r = hoje - timedelta(days=meta_receber.periodo_dias)
            total_para_meta_receber = Pedido.objects.filter(
                empresa=empresa
            ).exclude(status='CANCELADO').filter(
                data_pedido__gte=data_inicio_r, data_pedido__lte=hoje
            ).aggregate(s=Sum('valor_total'))['s'] or Decimal('0')
        if meta_lucro and meta_lucro.periodo_dias:
            data_inicio_l = hoje - timedelta(days=meta_lucro.periodo_dias)
            lucro_per = Pedido.objects.filter(
                empresa=empresa
            ).exclude(status='CANCELADO').filter(
                data_pedido__gte=data_inicio_l, data_pedido__lte=hoje
            ).aggregate(total=Sum(F('valor_total') - F('valor_custo')))['total']
            total_para_meta_lucro = Decimal(str(lucro_per)) if lucro_per is not None else Decimal('0')

    percent_receber = None
    if meta_receber and meta_receber.valor_meta > 0:
        p = float(total_para_meta_receber / meta_receber.valor_meta * 100)
        percent_receber = min(100, p) if p >= 0 else 0

    percent_lucro = None
    if meta_lucro and meta_lucro.valor_meta > 0:
        p = float(total_para_meta_lucro / meta_lucro.valor_meta * 100)
        percent_lucro = min(100, p) if p >= 0 else 0
    percent_producao = None
    if meta_producao and meta_producao.valor_meta > 0:
        p = float(total_para_meta_producao / meta_producao.valor_meta * 100)
        percent_producao = min(100, p) if p >= 0 else 0

    # Contas a pagar (acompanhamento no dashboard)
    contas_pagar_total_pendente = Decimal('0')
    contas_pagar_proximas = []
    contas_pagar_a_vencer = Decimal('0')
    contas_pagar_vencido = Decimal('0')
    contas_pagar_pago_mes = Decimal('0')
    try:
        from apps.contas.models import ContaPagar
        base_cp = ContaPagar.objects.filter(empresa=empresa, pago=False)
        contas_pagar_total_pendente = base_cp.aggregate(s=Sum('valor'))['s'] or Decimal('0')
        data_limite = hoje + timedelta(days=30)
        contas_pagar_proximas = list(
            base_cp.filter(data_vencimento__lte=data_limite)
            .select_related('fornecedor')
            .order_by('data_vencimento')[:15]
        )
        # Valores para o gráfico: A vencer, Vencido, Pago no mês
        contas_pagar_a_vencer = ContaPagar.objects.filter(
            empresa=empresa, pago=False, data_vencimento__gte=hoje
        ).aggregate(s=Sum('valor'))['s'] or Decimal('0')
        contas_pagar_vencido = ContaPagar.objects.filter(
            empresa=empresa, pago=False, data_vencimento__lt=hoje
        ).aggregate(s=Sum('valor'))['s'] or Decimal('0')
        primeiro_dia_mes = hoje.replace(day=1)
        contas_pagar_pago_mes = ContaPagar.objects.filter(
            empresa=empresa, pago=True,
            data_pagamento__gte=primeiro_dia_mes,
            data_pagamento__lte=hoje
        ).aggregate(s=Sum('valor'))['s'] or Decimal('0')
    except Exception:
        pass

    context = {
        'em_producao': em_producao,
        'em_producao_count': em_producao_count,
        'em_atraso': em_atraso,
        'em_atraso_count': em_atraso_count,
        'total_a_receber': total_a_receber,
        'total_a_pagar': total_a_pagar,
        'lucro': lucro,
        'total_pecas_produzidas': total_pecas_produzidas,
        'alertas_por_setor': alertas_por_setor,
        'dias_alerta_setor': dias_alerta,
        'pedidos_para_filtro': pedidos_para_filtro,
        'pedido_selecionado': pedido_selecionado,
        'meta_receber': meta_receber,
        'meta_lucro': meta_lucro,
        'meta_producao': meta_producao,
        'total_para_meta_receber': total_para_meta_receber,
        'total_para_meta_lucro': total_para_meta_lucro,
        'total_para_meta_producao': total_para_meta_producao,
        'percent_receber': percent_receber,
        'percent_lucro': percent_lucro,
        'percent_producao': percent_producao,
        'dias_ate_fim_do_ano': dias_ate_fim_do_ano,
        'ano_atual': hoje.year,
        'calendario': calendario,
        'contas_pagar_total_pendente': contas_pagar_total_pendente,
        'contas_pagar_proximas': contas_pagar_proximas,
        'contas_pagar_a_vencer': contas_pagar_a_vencer,
        'contas_pagar_vencido': contas_pagar_vencido,
        'contas_pagar_pago_mes': contas_pagar_pago_mes,
    }
    return render(request, 'pedidos/dashboard.html', context)


def _total_pecas_periodo(empresa, data_inicio, data_fim):
    """Soma quantidade de itens de pedidos não cancelados no período (data_pedido)."""
    from .models import ItemPedido
    r = ItemPedido.objects.filter(
        pedido__empresa=empresa,
        pedido__data_pedido__gte=data_inicio,
        pedido__data_pedido__lte=data_fim
    ).exclude(pedido__status='CANCELADO').aggregate(s=Sum('quantidade'))['s']
    return Decimal(str(r)) if r is not None else Decimal('0')


def _metas_dashboard_context(empresa):
    """Calcula dados das metas para exibição (total no período, percentual)."""
    hoje = tz.localdate()
    ativos = Pedido.objects.filter(empresa=empresa).exclude(status='CANCELADO')
    total_a_receber = ativos.filter(recebido=False).aggregate(s=Sum('valor_total'))['s'] or Decimal('0')
    lucro = ativos.aggregate(total=Sum(F('valor_total') - F('valor_custo')))['total']
    lucro = Decimal(str(lucro)) if lucro is not None else Decimal('0')
    total_pecas_geral = _total_pecas_periodo(empresa, hoje - timedelta(days=365 * 5), hoje)  # all time

    meta_receber = MetaValor.objects.filter(empresa=empresa, tipo='RECEBER').first()
    meta_lucro = MetaValor.objects.filter(empresa=empresa, tipo='LUCRO').first()
    meta_producao = MetaValor.objects.filter(empresa=empresa, tipo='PRODUCAO').first()

    total_para_meta_receber = total_a_receber
    total_para_meta_lucro = lucro
    total_para_meta_producao = total_pecas_geral
    if meta_receber and meta_receber.periodo_dias:
        data_inicio_r = hoje - timedelta(days=meta_receber.periodo_dias)
        total_para_meta_receber = Pedido.objects.filter(
            empresa=empresa
        ).exclude(status='CANCELADO').filter(
            data_pedido__gte=data_inicio_r, data_pedido__lte=hoje
        ).aggregate(s=Sum('valor_total'))['s'] or Decimal('0')
    if meta_lucro and meta_lucro.periodo_dias:
        data_inicio_l = hoje - timedelta(days=meta_lucro.periodo_dias)
        lucro_per = Pedido.objects.filter(
            empresa=empresa
        ).exclude(status='CANCELADO').filter(
            data_pedido__gte=data_inicio_l, data_pedido__lte=hoje
        ).aggregate(total=Sum(F('valor_total') - F('valor_custo')))['total']
        total_para_meta_lucro = Decimal(str(lucro_per)) if lucro_per is not None else Decimal('0')
    if meta_producao and meta_producao.periodo_dias:
        data_inicio_p = hoje - timedelta(days=meta_producao.periodo_dias)
        total_para_meta_producao = _total_pecas_periodo(empresa, data_inicio_p, hoje)

    percent_receber = None
    if meta_receber and meta_receber.valor_meta > 0:
        p = float(total_para_meta_receber / meta_receber.valor_meta * 100)
        percent_receber = min(100, p) if p >= 0 else 0
    percent_lucro = None
    if meta_lucro and meta_lucro.valor_meta > 0:
        p = float(total_para_meta_lucro / meta_lucro.valor_meta * 100)
        percent_lucro = min(100, p) if p >= 0 else 0
    percent_producao = None
    if meta_producao and meta_producao.valor_meta > 0:
        p = float(total_para_meta_producao / meta_producao.valor_meta * 100)
        percent_producao = min(100, p) if p >= 0 else 0

    return {
        'meta_receber': meta_receber,
        'meta_lucro': meta_lucro,
        'meta_producao': meta_producao,
        'total_para_meta_receber': total_para_meta_receber,
        'total_para_meta_lucro': total_para_meta_lucro,
        'total_para_meta_producao': total_para_meta_producao,
        'percent_receber': percent_receber,
        'percent_lucro': percent_lucro,
        'percent_producao': percent_producao,
    }


@login_required
def metas_dashboard(request):
    """Dashboard de visualização das metas (faturamento e lucro)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    ctx = _metas_dashboard_context(empresa)
    ctx['ano_atual'] = tz.localdate().year
    return render(request, 'pedidos/metas_dashboard.html', ctx)


@login_required
def metas_configurar(request):
    """Define metas de valor (a receber e lucro) – gestor."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        messages.error(request, 'Acesso restrito ao gestor.')
        return redirect('pedidos:dashboard')

    meta_receber_obj = MetaValor.objects.filter(empresa=empresa, tipo='RECEBER').first()
    meta_lucro_obj = MetaValor.objects.filter(empresa=empresa, tipo='LUCRO').first()
    meta_producao_obj = MetaValor.objects.filter(empresa=empresa, tipo='PRODUCAO').first()

    if request.method == 'POST':
        form = MetasValorForm(request.POST)
        if form.is_valid():
            meta_receber_val = form.cleaned_data.get('meta_receber') or Decimal('0')
            meta_lucro_val = form.cleaned_data.get('meta_lucro') or Decimal('0')
            meta_producao_val = form.cleaned_data.get('meta_producao') or Decimal('0')
            pr = form.cleaned_data.get('periodo_receber')
            pl = form.cleaned_data.get('periodo_lucro')
            pp = form.cleaned_data.get('periodo_producao')
            periodo_receber = int(pr) if pr and pr.isdigit() else None
            periodo_lucro = int(pl) if pl and pl.isdigit() else None
            periodo_producao = int(pp) if pp and pp.isdigit() else None
            MetaValor.objects.update_or_create(
                empresa=empresa, tipo='RECEBER',
                defaults={'valor_meta': meta_receber_val, 'periodo_dias': periodo_receber}
            )
            MetaValor.objects.update_or_create(
                empresa=empresa, tipo='LUCRO',
                defaults={'valor_meta': meta_lucro_val, 'periodo_dias': periodo_lucro}
            )
            MetaValor.objects.update_or_create(
                empresa=empresa, tipo='PRODUCAO',
                defaults={'valor_meta': meta_producao_val, 'periodo_dias': periodo_producao}
            )
            messages.success(request, 'Metas atualizadas com sucesso.')
            return redirect('pedidos:metas_dashboard')
    else:
        form = MetasValorForm(initial={
            'meta_receber': meta_receber_obj.valor_meta if meta_receber_obj else 0,
            'meta_lucro': meta_lucro_obj.valor_meta if meta_lucro_obj else 0,
            'meta_producao': meta_producao_obj.valor_meta if meta_producao_obj else 0,
            'periodo_receber': str(meta_receber_obj.periodo_dias) if meta_receber_obj and meta_receber_obj.periodo_dias is not None else '',
            'periodo_lucro': str(meta_lucro_obj.periodo_dias) if meta_lucro_obj and meta_lucro_obj.periodo_dias is not None else '',
            'periodo_producao': str(meta_producao_obj.periodo_dias) if meta_producao_obj and meta_producao_obj.periodo_dias is not None else '',
        })

    return render(request, 'pedidos/metas_configurar.html', {'form': form})


@login_required
def setores_lista(request):
    """Lista setores (gestor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        messages.error(request, 'Acesso restrito ao gestor.')
        return redirect('pedidos:dashboard')
    setores = Setor.objects.filter(empresa=empresa).order_by('ordem', 'nome')
    return render(request, 'pedidos/setores_lista.html', {'setores': setores})


@login_required
def setor_criar(request):
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('pedidos:dashboard')
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, f'Setor "{obj.nome}" criado.')
            return redirect('pedidos:setores_lista')
    else:
        form = SetorForm()
    return render(request, 'pedidos/setor_form.html', {'form': form, 'titulo': 'Novo setor'})


@login_required
def setor_editar(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('pedidos:dashboard')
    obj = get_object_or_404(Setor, pk=pk, empresa=empresa)
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Setor "{obj.nome}" atualizado.')
            return redirect('pedidos:setores_lista')
    else:
        form = SetorForm(instance=obj)
    return render(request, 'pedidos/setor_form.html', {'form': form, 'setor': obj, 'titulo': 'Editar setor'})


@login_required
def setor_excluir(request, pk):
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('pedidos:dashboard')
    obj = get_object_or_404(Setor, pk=pk, empresa=empresa)
    if request.method == 'POST':
        nome = obj.nome
        obj.delete()
        messages.success(request, f'Setor "{nome}" excluído.')
        return redirect('pedidos:setores_lista')
    return render(request, 'pedidos/setor_confirmar_exclusao.html', {'setor': obj})


def _queryset_em_atraso(empresa):
    """Pedidos em atraso: por setor ou por pedido completo (exclui cancelados)."""
    from django.utils import timezone
    hoje = timezone.localdate()
    q_atraso = (
        Q(status='EM_PRODUCAO', data_prevista_entrega__lt=hoje)
        | (Q(data_prevista_entrega_completo__lt=hoje, data_prevista_entrega_completo__isnull=False) & ~Q(status='ENTREGUE'))
    )
    return Pedido.objects.filter(empresa=empresa).filter(q_atraso).exclude(status='CANCELADO').distinct()


@login_required
def pedidos_lista(request):
    """Lista todos os pedidos."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    qs = Pedido.objects.filter(empresa=empresa).select_related(
        'cliente', 'setor_atual'
    ).order_by('-criado_em')
    status_filtro = request.GET.get('status', '')
    atraso_filtro = request.GET.get('atraso') == '1'
    if atraso_filtro:
        qs = _queryset_em_atraso(empresa).select_related('cliente', 'setor_atual').order_by(
            'data_prevista_entrega', 'data_prevista_entrega_completo', '-criado_em'
        )
    elif status_filtro:
        qs = qs.filter(status=status_filtro)
    pedidos = qs[:200]
    return render(request, 'pedidos/pedidos_lista.html', {
        'pedidos': pedidos,
        'status_filtro': status_filtro,
        'atraso_filtro': atraso_filtro,
    })


@login_required
def pedidos_acompanhamento(request):
    """Página de acompanhamento: visualizar pedidos por status (Rascunho, Em produção, Entregue, Cancelado)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    qs = Pedido.objects.filter(empresa=empresa).select_related(
        'cliente', 'setor_atual'
    ).order_by('-criado_em')[:300]
    pedidos_rascunho = [p for p in qs if p.status == 'RASCUNHO']
    pedidos_em_producao = [p for p in qs if p.status == 'EM_PRODUCAO']
    pedidos_entregues = [p for p in qs if p.status == 'ENTREGUE']
    pedidos_cancelados = [p for p in qs if p.status == 'CANCELADO']
    return render(request, 'pedidos/pedidos_acompanhamento.html', {
        'pedidos_rascunho': pedidos_rascunho,
        'pedidos_em_producao': pedidos_em_producao,
        'pedidos_entregues': pedidos_entregues,
        'pedidos_cancelados': pedidos_cancelados,
    })


@login_required
def pedido_criar(request):
    from django.utils import timezone
    from apps.produtos.models import Produto

    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')

    produtos = Produto.objects.filter(empresa=empresa, ativo=True).order_by('nome')
    itens_rascunho = _itens_rascunho(request)
    total_receber, total_custo = _totais_rascunho(itens_rascunho)

    if request.method == 'POST':
        form = PedidoForm(request.POST, empresa=empresa)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            if itens_rascunho:
                obj.valor_total = total_receber
                obj.valor_custo = total_custo
            # Ao salvar novo pedido, vai para "Em produção"
            obj.status = 'EM_PRODUCAO'
            if obj.setor_atual:
                obj.data_entrada_setor = timezone.now()
            obj.save()
            # Criar itens do pedido a partir do rascunho na sessão
            for item in itens_rascunho:
                ItemPedido.objects.create(
                    pedido=obj,
                    produto_id=item['produto_id'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco_unitario'],
                    preco_custo_unitario=item['preco_custo_unitario'],
                    tamanhos=item.get('tamanhos', ''),
                )
            if itens_rascunho:
                obj.recalcular_totais_dos_itens()
            request.session.pop(SESSION_RASCUNHO_ITENS, None)
            request.session.pop(SESSION_RASCUNHO_HEADER, None)
            request.session.modified = True
            messages.success(request, f'Pedido #{obj.numero} criado com sucesso.')
            url_lista = request.build_absolute_uri(reverse('pedidos:pedidos_lista') + '?status=EM_PRODUCAO')
            return HttpResponseRedirect(url_lista)
    else:
        initial = dict(request.session.get(SESSION_RASCUNHO_HEADER, {}))
        if itens_rascunho:
            initial['valor_total'] = total_receber
            initial['valor_custo'] = total_custo
        else:
            initial.setdefault('valor_total', Decimal('0'))
            initial.setdefault('valor_custo', Decimal('0'))
        form = PedidoForm(empresa=empresa, initial=initial)

    # Calcular subtotal de cada item do rascunho para exibição
    itens_rascunho_exibir = []
    for i in itens_rascunho:
        q = float(i['quantidade'])
        pu = float(i['preco_unitario'])
        itens_rascunho_exibir.append({**i, 'subtotal': f'{(q * pu):.2f}'})
    return render(request, 'pedidos/pedido_form.html', {
        'form': form,
        'titulo': 'Novo pedido',
        'pedido': None,
        'itens': [],
        'produtos': produtos,
        'itens_rascunho': itens_rascunho_exibir,
        'total_rascunho_receber': total_receber,
        'total_rascunho_custo': total_custo,
        'total_rascunho_lucro': total_receber - total_custo,
        'tamanhos_por_categoria': TAMANHOS_POR_CATEGORIA,
    })


@login_required
def pedido_rascunho_item_adicionar(request):
    """Adiciona um produto ao rascunho do novo pedido (sessão)."""
    from apps.produtos.models import Produto

    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    produto_id = request.POST.get('produto_id')
    quantidade = request.POST.get('quantidade', '1').replace(',', '.')
    if not produto_id:
        messages.error(request, 'Selecione um produto.')
        return redirect('pedidos:pedido_criar')
    try:
        qtd = abs(float(quantidade))
        if qtd <= 0:
            raise ValueError('Quantidade inválida')
    except (ValueError, TypeError):
        messages.error(request, 'Quantidade inválida.')
        return redirect('pedidos:pedido_criar')
    produto = get_object_or_404(Produto, pk=produto_id, empresa=empresa)
    tamanhos_list = [s.strip() for s in request.POST.getlist('tamanhos_item') if s and s.strip()]
    if not tamanhos_list:
        tamanhos_list = ['']  # um único item sem tamanho
    itens = _itens_rascunho(request)
    # Uma linha por tamanho: para cada tamanho, adiciona ou soma na linha (produto + tamanho)
    for tam in tamanhos_list:
        tam_str = tam if tam else ''
        encontrado = False
        for i in itens:
            if i['produto_id'] == produto.pk and (i.get('tamanhos') or '') == tam_str:
                i['quantidade'] = float(i['quantidade']) + qtd
                encontrado = True
                break
        if not encontrado:
            itens.append({
                'produto_id': produto.pk,
                'produto_nome': produto.nome,
                'produto_unidade': produto.unidade,
                'quantidade': qtd,
                'preco_unitario': str(produto.preco_venda),
                'preco_custo_unitario': str(produto.preco_custo or 0),
                'tamanhos': tam_str,
            })
    request.session[SESSION_RASCUNHO_ITENS] = itens
    # Guardar dados do cabeçalho do pedido (cliente, status, setor, datas, etc.) para manter ao voltar
    header_keys = ['cliente', 'status', 'setor_atual', 'data_pedido', 'data_prevista_entrega', 'data_prevista_entrega_completo', 'forma_pagamento', 'prazo']
    request.session[SESSION_RASCUNHO_HEADER] = {k: request.POST.get(k, '') for k in header_keys}
    request.session.modified = True
    msg = f'"{produto.nome}" adicionado ao pedido'
    if len(tamanhos_list) > 1 or (len(tamanhos_list) == 1 and tamanhos_list[0]):
        msg += f' ({len(tamanhos_list)} tamanho(s))'
    messages.success(request, msg + '.', extra_tags='toast')
    return redirect('pedidos:pedido_criar')


@login_required
def pedido_rascunho_item_remover(request, indice):
    """Remove um item do rascunho do novo pedido (sessão)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    itens = _itens_rascunho(request)
    indice = int(indice)
    if 0 <= indice < len(itens):
        itens.pop(indice)
        request.session[SESSION_RASCUNHO_ITENS] = itens
        request.session.modified = True
        messages.success(request, 'Produto removido do pedido.')
    return redirect('pedidos:pedido_criar')


@login_required
def pedido_editar(request, pk):
    from django.utils import timezone
    from apps.produtos.models import Produto

    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    setor_anterior_id = pedido.setor_atual_id if pedido.pk else None
    itens = list(pedido.itens.select_related('produto').all())
    produtos = Produto.objects.filter(empresa=empresa, ativo=True).order_by('nome')

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido, empresa=empresa)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.setor_atual_id != setor_anterior_id and obj.setor_atual_id:
                obj.data_entrada_setor = timezone.now()
            if obj.setor_atual_id and obj.status == 'RASCUNHO':
                obj.status = 'EM_PRODUCAO'
            obj.save()
            # Totais vêm dos itens quando existirem
            if obj.itens.exists():
                obj.recalcular_totais_dos_itens()
            messages.success(request, f'Pedido #{pedido.numero} atualizado.')
            url_lista = request.build_absolute_uri(reverse('pedidos:pedidos_lista') + '?status=' + obj.status)
            return HttpResponseRedirect(url_lista)
    else:
        form = PedidoForm(instance=pedido, empresa=empresa)

    return render(request, 'pedidos/pedido_form.html', {
        'form': form,
        'pedido': pedido,
        'titulo': f'Editar pedido #{pedido.numero}',
        'itens': itens,
        'produtos': produtos,
        'itens_rascunho': [],
        'tamanhos_por_categoria': TAMANHOS_POR_CATEGORIA,
    })


@login_required
def pedido_excluir(request, pk):
    """Exclui um pedido."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    if request.method == 'POST':
        numero = pedido.numero
        pedido.delete()
        messages.success(request, f'Pedido #{numero} excluído.')
        return redirect('pedidos:pedidos_lista')
    return redirect('pedidos:pedidos_lista')


@login_required
def pedido_acompanhar(request, pk):
    """Página para acompanhar o pedido e alterar setor/status (ex.: Desenvolvimento → Costura)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('itens__produto'),
        pk=pk, empresa=empresa
    )
    setores = Setor.objects.filter(empresa=empresa, ativo=True).order_by('ordem', 'nome')

    if request.method == 'POST':
        # Alterar status do pedido
        novo_status = request.POST.get('status')
        if novo_status and novo_status in dict(STATUS_PEDIDO):
            pedido.status = novo_status
            pedido.save(update_fields=['status'])
            messages.success(request, f'Status do pedido #{pedido.numero} atualizado.')
            return redirect('pedidos:pedido_acompanhar', pk=pedido.pk)

    return render(request, 'pedidos/pedido_acompanhar.html', {
        'pedido': pedido,
        'setores': setores,
        'status_choices': STATUS_PEDIDO,
    })


@login_required
def pedido_mover_setor(request, pk):
    """Marca entrada no setor atual (atualiza data_entrada_setor ao trocar setor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    setor_id = request.POST.get('setor_id')
    if setor_id:
        from django.utils import timezone
        novo_setor = get_object_or_404(Setor, pk=int(setor_id), empresa=empresa)
        pedido.setor_atual = novo_setor
        pedido.data_entrada_setor = timezone.now()
        if pedido.status == 'RASCUNHO':
            pedido.status = 'EM_PRODUCAO'
        pedido.save()
        messages.success(request, f'Pedido #{pedido.numero} movido para {novo_setor.nome}.')
    if request.POST.get('next') == 'acompanhar' or request.GET.get('next') == 'acompanhar':
        return redirect('pedidos:pedido_acompanhar', pk=pk)
    return redirect('pedidos:pedidos_lista')


@login_required
def pedido_item_adicionar(request, pk):
    """Adiciona um produto ao pedido (ou soma na quantidade se já existir)."""
    from apps.produtos.models import Produto

    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    produto_id = request.POST.get('produto_id')
    quantidade = request.POST.get('quantidade', '1').replace(',', '.')
    if not produto_id:
        messages.error(request, 'Selecione um produto.')
        return redirect('pedidos:pedido_editar', pk=pedido.pk)
    try:
        qtd = abs(float(quantidade))
        if qtd <= 0:
            raise ValueError('Quantidade inválida')
    except (ValueError, TypeError):
        messages.error(request, 'Quantidade inválida.')
        return redirect('pedidos:pedido_editar', pk=pedido.pk)
    produto = get_object_or_404(Produto, pk=produto_id, empresa=empresa)
    tamanhos_list = [s.strip() for s in request.POST.getlist('tamanhos_item') if s and s.strip()]
    if not tamanhos_list:
        tamanhos_list = ['']  # um único item sem tamanho
    # Uma linha por tamanho no pedido
    for tam in tamanhos_list:
        tam_str = tam if tam else ''
        item, created = ItemPedido.objects.get_or_create(
            pedido=pedido,
            produto=produto,
            tamanhos=tam_str,
            defaults={
                'quantidade': qtd,
                'preco_unitario': produto.preco_venda,
                'preco_custo_unitario': produto.preco_custo or Decimal('0'),
            }
        )
        if not created:
            item.quantidade += qtd
            item.save(update_fields=['quantidade'])
    pedido.recalcular_totais_dos_itens()
    messages.success(request, f'"{produto.nome}" adicionado ao pedido.', extra_tags='toast')
    return redirect('pedidos:pedido_editar', pk=pedido.pk)


@login_required
def pedido_item_remover(request, pk, item_pk):
    """Remove um item do pedido."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    item = get_object_or_404(ItemPedido, pk=item_pk, pedido=pedido)
    nome = item.produto.nome
    item.delete()
    pedido.recalcular_totais_dos_itens()
    messages.success(request, f'"{nome}" removido do pedido.')
    return redirect('pedidos:pedido_editar', pk=pedido.pk)


@login_required
def pedido_item_alterar_qtd(request, pk, item_pk):
    """Altera a quantidade de um item do pedido."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    pedido = get_object_or_404(Pedido, pk=pk, empresa=empresa)
    item = get_object_or_404(ItemPedido, pk=item_pk, pedido=pedido)
    quantidade = request.POST.get('quantidade', '').replace(',', '.')
    try:
        qtd = abs(float(quantidade))
        if qtd <= 0:
            item.delete()
            pedido.recalcular_totais_dos_itens()
            messages.success(request, f'Item removido (quantidade zerada).')
            return redirect('pedidos:pedido_editar', pk=pedido.pk)
    except (ValueError, TypeError):
        messages.error(request, 'Quantidade inválida.')
        return redirect('pedidos:pedido_editar', pk=pedido.pk)
    item.quantidade = qtd
    item.save(update_fields=['quantidade'])
    pedido.recalcular_totais_dos_itens()
    messages.success(request, f'Quantidade de "{item.produto.nome}" atualizada.')
    return redirect('pedidos:pedido_editar', pk=pedido.pk)
