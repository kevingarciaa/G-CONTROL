"""
Formulários para Fornecedor.
"""
from django import forms
from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    """Formulário de cadastro/edição de fornecedor."""

    class Meta:
        model = Fornecedor
        fields = ['nome', 'segmento', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome ou razão social'}),
            'segmento': forms.Select(attrs={'class': 'form-select'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF ou CNPJ'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Endereço'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
