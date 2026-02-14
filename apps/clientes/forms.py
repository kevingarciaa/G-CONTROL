"""
Formulários para Cliente.
"""
from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """Formulário de cadastro/edição de cliente."""

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF ou CNPJ'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Endereço'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
