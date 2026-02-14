"""
Formulários para FormaPagamento.
"""
from django import forms
from .models import FormaPagamento


class FormaPagamentoForm(forms.ModelForm):
    """Formulário de cadastro/edição de forma de pagamento."""

    class Meta:
        model = FormaPagamento
        fields = ['nome', 'taxa_percentual', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Dinheiro, PIX, Cartão'}),
            'taxa_percentual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
