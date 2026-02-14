from datetime import timedelta
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from apps.fornecedores.models import Fornecedor
from .models import ContaPagar
from .forms import ContaPagarForm


def _empresa(request):
    return getattr(request.user, 'empresa', None)


@login_required
def lista(request):
    """Lista de contas a pagar da empresa."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')

    qs = ContaPagar.objects.filter(empresa=empresa).select_related('fornecedor').order_by('-data_vencimento', '-criado_em')

    filtro = (request.GET.get('filtro') or '').strip()
    if filtro == 'pago':
        qs = qs.filter(pago=True)
    elif filtro == 'pendente':
        qs = qs.filter(pago=False)

    periodo = (request.GET.get('periodo') or '').strip()
    hoje = timezone.localdate()
    periodo_label = None
    if periodo == '7':
        data_fim = hoje + timedelta(days=7)
        qs = qs.filter(data_vencimento__gte=hoje, data_vencimento__lte=data_fim)
        periodo_label = 'Próximos 7 dias'
    elif periodo == '15':
        data_fim = hoje + timedelta(days=15)
        qs = qs.filter(data_vencimento__gte=hoje, data_vencimento__lte=data_fim)
        periodo_label = 'Próximos 15 dias'
    elif periodo == '30':
        data_fim = hoje + timedelta(days=30)
        qs = qs.filter(data_vencimento__gte=hoje, data_vencimento__lte=data_fim)
        periodo_label = 'Próximos 30 dias'
    elif periodo == 'semana':
        # Segunda a domingo da semana atual
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        qs = qs.filter(data_vencimento__gte=inicio_semana, data_vencimento__lte=fim_semana)
        periodo_label = 'Esta semana'
    elif periodo == 'mes':
        inicio_mes = hoje.replace(day=1)
        _, ultimo_dia = monthrange(hoje.year, hoje.month)
        fim_mes = hoje.replace(day=ultimo_dia)
        qs = qs.filter(data_vencimento__gte=inicio_mes, data_vencimento__lte=fim_mes)
        periodo_label = 'Este mês'

    busca = (request.GET.get('q') or '').strip()
    if busca:
        qs = qs.filter(
            Q(descricao__icontains=busca) |
            Q(observacao__icontains=busca) |
            Q(fornecedor__nome__icontains=busca)
        )

    contas = qs[:300]

    total_pendente = ContaPagar.objects.filter(empresa=empresa, pago=False).aggregate(
        s=Sum('valor')
    )['s'] or 0

    return render(request, 'contas/lista.html', {
        'contas': contas,
        'busca': busca,
        'filtro': filtro,
        'periodo': periodo,
        'periodo_label': periodo_label,
        'total_pendente': total_pendente,
    })


@login_required
def conta_criar(request):
    """Cria uma nova conta a pagar."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if request.method == 'POST':
        form = ContaPagarForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, f'Conta "{obj.descricao}" cadastrada.')
            return redirect('contas:lista')
    else:
        form = ContaPagarForm()
    form.fields['fornecedor'].queryset = Fornecedor.objects.filter(empresa=empresa).order_by('nome')
    return render(request, 'contas/conta_form.html', {'form': form, 'titulo': 'Nova conta a pagar'})


@login_required
def conta_editar(request, pk):
    """Edita uma conta a pagar."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    conta = get_object_or_404(ContaPagar, pk=pk, empresa=empresa)
    if request.method == 'POST':
        form = ContaPagarForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conta "{conta.descricao}" atualizada.')
            return redirect('contas:lista')
    else:
        form = ContaPagarForm(instance=conta)
    form.fields['fornecedor'].queryset = Fornecedor.objects.filter(empresa=empresa).order_by('nome')
    return render(request, 'contas/conta_form.html', {
        'form': form, 'conta': conta, 'titulo': 'Editar conta a pagar'
    })


@login_required
def conta_excluir(request, pk):
    """Exclui uma conta a pagar."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    conta = get_object_or_404(ContaPagar, pk=pk, empresa=empresa)
    if request.method == 'POST':
        descricao = conta.descricao
        conta.delete()
        messages.success(request, f'Conta "{descricao}" excluída.')
        return redirect('contas:lista')
    return render(request, 'contas/conta_confirmar_exclusao.html', {'conta': conta})


@login_required
def conta_marcar_pago(request, pk):
    """Marca a conta como paga (ou desmarca)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    conta = get_object_or_404(ContaPagar, pk=pk, empresa=empresa)
    if request.method == 'POST':
        conta.pago = not conta.pago
        conta.data_pagamento = timezone.localdate() if conta.pago else None
        conta.save()
        if conta.pago:
            messages.success(request, f'Conta "{conta.descricao}" marcada como paga.')
        else:
            messages.info(request, f'Conta "{conta.descricao}" marcada como pendente.')
        return redirect('contas:lista')
    return redirect('contas:lista')
