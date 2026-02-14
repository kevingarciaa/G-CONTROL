"""
Regras de desconto, promoções e taxas por forma de pagamento.
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone


class RegraDesconto(models.Model):
    """Regra de desconto (ex: 10% em bebidas, R$ 5 em compras acima de R$ 50)."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='regras_desconto'
    )
    nome = models.CharField('Nome da regra', max_length=100)
    tipo = models.CharField(
        max_length=10,
        choices=[
            ('PERCENTUAL', 'Percentual (%)'),
            ('VALOR', 'Valor fixo (R$)'),
        ],
        default='PERCENTUAL'
    )
    valor = models.DecimalField('Valor (%) ou (R$)', max_digits=10, decimal_places=2, default=0)
    valor_minimo_pedido = models.DecimalField(
        'Valor mínimo do pedido (R$)',
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True
    )
    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='regras_desconto'
    )
    ativo = models.BooleanField('Ativo', default=True)
    data_inicio = models.DateTimeField('Início', null=True, blank=True)
    data_fim = models.DateTimeField('Fim', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Regra de desconto'
        verbose_name_plural = 'Regras de desconto'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    def vigente(self):
        now = timezone.now()
        if self.data_inicio and now < self.data_inicio:
            return False
        if self.data_fim and now > self.data_fim:
            return False
        return True

    def calcular_desconto(self, valor_item, quantidade=1):
        total_item = valor_item * quantidade
        if self.valor_minimo_pedido and total_item < self.valor_minimo_pedido:
            return Decimal('0')
        if self.tipo == 'PERCENTUAL':
            return (total_item * self.valor / 100).quantize(Decimal('0.01'))
        return min(self.valor, total_item)


class FormaPagamento(models.Model):
    """Forma de pagamento (Dinheiro, Cartão, PIX) com opção de taxa."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='formas_pagamento'
    )
    nome = models.CharField('Nome', max_length=50)  # Dinheiro, Débito, Crédito, PIX
    taxa_percentual = models.DecimalField(
        'Taxa (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Taxa aplicada sobre o valor (ex: 2.5 para 2,5%)'
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Forma de pagamento'
        verbose_name_plural = 'Formas de pagamento'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def calcular_taxa(self, valor):
        return (valor * self.taxa_percentual / 100).quantize(Decimal('0.01'))
