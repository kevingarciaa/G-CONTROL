from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm


def _empresa(request):
    return getattr(request.user, 'empresa', None)


@login_required
def cadastro(request):
    """Página de Cadastro: Clientes e Fornecedores."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    return render(request, 'clientes/cadastro.html')


@login_required
def lista(request):
    """Lista de clientes da empresa."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    clientes = Cliente.objects.filter(empresa=empresa).order_by('nome')

    busca = (request.GET.get('q') or '').strip()
    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(cpf_cnpj__icontains=busca) |
            Q(email__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(endereco__icontains=busca)
        )

    return render(request, 'clientes/lista.html', {'clientes': clientes, 'busca': busca})


@login_required
def cliente_criar(request):
    """Cria um novo cliente."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, f'Cliente "{obj.nome}" cadastrado com sucesso.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form, 'titulo': 'Novo cliente'})


@login_required
def cliente_editar(request, pk):
    """Edita um cliente existente."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    cliente = get_object_or_404(Cliente, pk=pk, empresa=empresa)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{cliente.nome}" atualizado.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'cliente': cliente, 'titulo': 'Editar cliente'})


@login_required
def cliente_excluir(request, pk):
    """Exclui um cliente."""
    empresa = _empresa(request)
    if not empresa:
        return redirect('logout')
    cliente = get_object_or_404(Cliente, pk=pk, empresa=empresa)
    if request.method == 'POST':
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" excluído.')
        return redirect('clientes:lista')
    return render(request, 'clientes/cliente_confirmar_exclusao.html', {'cliente': cliente})
