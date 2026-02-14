"""
Formulários para Produto.
"""
from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    """Formulário de cadastro/edição de produto."""

    class Meta:
        model = Produto
        fields = [
            'nome', 'codigo_barras', 'referencia_pedido', 'referencia_cliente',
            'gramas_por_metro', 'valor_tecido',
            'quantidade_estamparia', 'valor_unitario_estamparia',
            'quantidade_acabamento', 'valor_unitario_acabamento',
            'quantidade_aviamentos', 'valor_unitario_aviamentos',
            'quantidade_costura', 'valor_unitario_costura',
            'quantidade_outros', 'valor_unitario_outros',
            'preco_venda', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de barras'}),
            'referencia_pedido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Pedido #123'}),
            'referencia_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Nome ou código do cliente'}),
            'gramas_por_metro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 0,200', 'id': 'id_gramas_por_metro'}),
            'valor_tecido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex.: 42,00', 'id': 'id_valor_tecido'}),
            'quantidade_estamparia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 1', 'id': 'id_quantidade_estamparia'}),
            'valor_unitario_estamparia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$', 'id': 'id_valor_unitario_estamparia'}),
            'quantidade_acabamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 1', 'id': 'id_quantidade_acabamento'}),
            'valor_unitario_acabamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$', 'id': 'id_valor_unitario_acabamento'}),
            'quantidade_aviamentos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 1', 'id': 'id_quantidade_aviamentos'}),
            'valor_unitario_aviamentos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$', 'id': 'id_valor_unitario_aviamentos'}),
            'quantidade_costura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 1', 'id': 'id_quantidade_costura'}),
            'valor_unitario_costura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$', 'id': 'id_valor_unitario_costura'}),
            'quantidade_outros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Ex.: 1', 'id': 'id_quantidade_outros'}),
            'valor_unitario_outros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$', 'id': 'id_valor_unitario_outros'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'R$ 0,00', 'id': 'id_preco_venda'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
