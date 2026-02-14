from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Fornecedor
from .forms import FornecedorForm


def _empresa(request):
    return getattr(request.user, 'empresa', None)


@login_required
def lista(request):
    """Lista de fornecedores da empresa."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    fornecedores = Fornecedor.objects.filter(empresa=empresa).order_by('nome')

    busca = (request.GET.get('q') or '').strip()
    if busca:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=busca) |
            Q(cpf_cnpj__icontains=busca) |
            Q(email__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(endereco__icontains=busca)
        )

    return render(request, 'fornecedores/lista.html', {'fornecedores': fornecedores, 'busca': busca})


@login_required
def fornecedor_criar(request):
    """Cria um novo fornecedor."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, f'Fornecedor "{obj.nome}" cadastrado com sucesso.')
            return redirect('fornecedores:lista')
    else:
        form = FornecedorForm()
    return render(request, 'fornecedores/fornecedor_form.html', {'form': form, 'titulo': 'Novo fornecedor'})


@login_required
def fornecedor_editar(request, pk):
    """Edita um fornecedor existente."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=empresa)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fornecedor "{fornecedor.nome}" atualizado.')
            return redirect('fornecedores:lista')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'fornecedores/fornecedor_form.html', {
        'form': form, 'fornecedor': fornecedor, 'titulo': 'Editar fornecedor'
    })


@login_required
def fornecedor_excluir(request, pk):
    """Exclui um fornecedor."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=empresa)
    if request.method == 'POST':
        nome = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome}" excluído.')
        return redirect('fornecedores:lista')
    return render(request, 'fornecedores/fornecedor_confirmar_exclusao.html', {'fornecedor': fornecedor})
