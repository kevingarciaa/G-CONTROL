"""
Formas de pagamento - CRUD no frontend (gestor).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FormaPagamento
from .forms import FormaPagamentoForm


def _empresa(request):
    return getattr(request.user, 'empresa', None)


@login_required
def formas_lista(request):
    """Lista formas de pagamento (gestor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        messages.error(request, 'Acesso restrito ao gestor.')
        return redirect('produtos:lista')
    formas = FormaPagamento.objects.filter(empresa=empresa).order_by('nome')
    return render(request, 'promocoes/formas.html', {'formas': formas})


@login_required
def forma_criar(request):
    """Cria nova forma de pagamento (gestor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('produtos:lista')
    if request.method == 'POST':
        form = FormaPagamentoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, f'Forma "{obj.nome}" cadastrada.')
            return redirect('promocoes:formas')
    else:
        form = FormaPagamentoForm()
    return render(request, 'promocoes/forma_form.html', {'form': form, 'titulo': 'Nova forma de pagamento'})


@login_required
def forma_editar(request, pk):
    """Edita forma de pagamento (gestor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('produtos:lista')
    forma = get_object_or_404(FormaPagamento, pk=pk, empresa=empresa)
    if request.method == 'POST':
        form = FormaPagamentoForm(request.POST, instance=forma)
        if form.is_valid():
            form.save()
            messages.success(request, f'Forma "{forma.nome}" atualizada.')
            return redirect('promocoes:formas')
    else:
        form = FormaPagamentoForm(instance=forma)
    return render(request, 'promocoes/forma_form.html', {'form': form, 'forma': forma, 'titulo': 'Editar forma de pagamento'})


@login_required
def forma_excluir(request, pk):
    """Exclui forma de pagamento (gestor)."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if not request.user.is_gestor:
        return redirect('produtos:lista')
    forma = get_object_or_404(FormaPagamento, pk=pk, empresa=empresa)
    if request.method == 'POST':
        nome = forma.nome
        forma.delete()
        messages.success(request, f'Forma "{nome}" excluída.')
        return redirect('promocoes:formas')
    return render(request, 'promocoes/forma_confirmar_exclusao.html', {'forma': forma})
