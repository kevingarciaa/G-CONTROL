from django import forms
from .models import Setor, Pedido, MetaValor, PERIODO_META_CHOICES
from apps.promocoes.models import FormaPagamento


TAMANHOS_CHOICES = [
    ('PP', 'PP'), ('P', 'P'), ('M', 'M'), ('G', 'G'), ('GG', 'GG'),
    ('XG', 'XG'), ('XXG', 'XXG'),
    ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40'), ('42', '42'),
    ('44', '44'), ('46', '46'), ('48', '48'), ('50', '50'),
    ('Único', 'Único'),
]

# Duas caixas: Camiseta (letras) e Calça/Shorts (numérico)
TAMANHOS_POR_CATEGORIA = [
    ('Camiseta', [('PP', 'PP'), ('P', 'P'), ('M', 'M'), ('G', 'G'), ('GG', 'GG'), ('XG', 'XG'), ('XXG', 'XXG')]),
    ('Calça / Shorts / Numérico', [('34', '34'), ('36', '36'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('46', '46'), ('48', '48'), ('50', '50'), ('Único', 'Único')]),
]


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome', 'ordem', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Corte, Costura'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente', 'status', 'setor_atual', 'data_pedido',
            'data_prevista_entrega', 'data_prevista_entrega_completo', 'valor_total', 'valor_custo',
            'forma_pagamento', 'prazo'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'setor_atual': forms.Select(attrs={'class': 'form-select'}),
            'data_pedido': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_prevista_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_prevista_entrega_completo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'form': 'pedido-form'}),
            'valor_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'form': 'pedido-form'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'prazo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if self.empresa:
            self.fields['cliente'].queryset = self.fields['cliente'].queryset.filter(
                empresa=self.empresa, ativo=True
            ).order_by('nome')
            self.fields['setor_atual'].queryset = Setor.objects.filter(
                empresa=self.empresa, ativo=True
            ).order_by('ordem', 'nome')
            self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(
                empresa=self.empresa, ativo=True
            ).order_by('nome')
            self.fields['forma_pagamento'].empty_label = 'Selecione...'


def _periodo_choices():
    return [( '', 'Todo o período' )] + [( str(k), v ) for k, v in PERIODO_META_CHOICES if k is not None]


class MetasValorForm(forms.Form):
    """Formulário para definir metas a receber e de lucro, com período editável."""
    meta_receber = forms.DecimalField(
        label='Meta a receber (R$)',
        max_digits=12,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0,00'})
    )
    periodo_receber = forms.ChoiceField(
        label='Período (meta a receber)',
        required=False,
        choices=_periodo_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    meta_lucro = forms.DecimalField(
        label='Meta de lucro (R$)',
        max_digits=12,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0,00'})
    )
    periodo_lucro = forms.ChoiceField(
        label='Período (meta de lucro)',
        required=False,
        choices=_periodo_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    meta_producao = forms.DecimalField(
        label='Meta de produção (peças)',
        max_digits=12,
        decimal_places=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'placeholder': '0'})
    )
    periodo_producao = forms.ChoiceField(
        label='Período (meta de produção)',
        required=False,
        choices=_periodo_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
