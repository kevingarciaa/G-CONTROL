"""
Contas a pagar da empresa.
"""
from decimal import Decimal
from django.db import models


class ContaPagar(models.Model):
    """Conta a pagar (despesa, fornecedor, etc.)."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='contas_pagar'
    )
    descricao = models.CharField('Descrição', max_length=200)
    valor = models.DecimalField(
        'Valor (R$)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    data_vencimento = models.DateField('Data de vencimento')
    pago = models.BooleanField('Pago', default=False)
    data_pagamento = models.DateField('Data do pagamento', null=True, blank=True)
    fornecedor = models.ForeignKey(
        'fornecedores.Fornecedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name='Fornecedor'
    )
    observacao = models.CharField('Observação', max_length=500, blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Conta a pagar'
        verbose_name_plural = 'Contas a pagar'
        ordering = ['-data_vencimento', '-criado_em']

    def __str__(self):
        return f'{self.descricao} — R$ {self.valor}'
