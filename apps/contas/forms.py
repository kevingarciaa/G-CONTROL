"""
Formulários para Conta a pagar.
"""
from django import forms
from .models import ContaPagar


class ContaPagarForm(forms.ModelForm):
    """Formulário de cadastro/edição de conta a pagar."""

    class Meta:
        model = ContaPagar
        fields = [
            'descricao', 'valor', 'data_vencimento',
            'pago', 'data_pagamento', 'fornecedor', 'observacao'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Compra tecido, Serviço costura'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pago': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações'}),
        }
