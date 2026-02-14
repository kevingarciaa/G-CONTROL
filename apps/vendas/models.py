"""
Vendas, itens de venda e listas de pedidos.
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone


class Venda(models.Model):
    """Venda (pedido finalizado)."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='vendas'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendas'
    )
    vendedor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='vendas_realizadas'
    )
    numero = models.PositiveIntegerField('Número', editable=False, default=0)  # sequencial por empresa
    desconto_total = models.DecimalField(
        'Desconto (R$)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    taxa_pagamento = models.DecimalField(
        'Taxa pagamento (R$)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    total = models.DecimalField('Total (R$)', max_digits=12, decimal_places=2, default=0)
    forma_pagamento = models.ForeignKey(
        'promocoes.FormaPagamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendas'
    )
    criado_em = models.DateTimeField('Data/hora', default=timezone.now)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Venda #{self.numero} - {self.criado_em.strftime("%d/%m/%Y %H:%M")}'

    def save(self, *args, **kwargs):
        if self.pk is None and self.empresa_id:
            ultima = Venda.objects.filter(empresa=self.empresa).order_by('-numero').first()
            self.numero = (ultima.numero + 1) if ultima else 1
        super().save(*args, **kwargs)


class ItemVenda(models.Model):
    """Item de uma venda."""
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.PROTECT,
        related_name='itens_venda'
    )
    quantidade = models.DecimalField('Quantidade', max_digits=12, decimal_places=3, default=1)
    preco_unitario = models.DecimalField('Preço unit.', max_digits=12, decimal_places=2)
    desconto = models.DecimalField('Desconto (R$)', max_digits=12, decimal_places=2, default=Decimal('0'))
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Item de venda'
        verbose_name_plural = 'Itens de venda'

    def __str__(self):
        return f'{self.produto.nome} x {self.quantidade}'


class ListaPedido(models.Model):
    """Lista de pedido/compra do cliente (carrinho ou pedido em andamento)."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='listas_pedido'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listas_pedido'
    )
    vendedor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='listas_pedido'
    )
    nome = models.CharField('Nome da lista', max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    finalizada = models.BooleanField('Finalizada (virou venda)', default=False)

    class Meta:
        verbose_name = 'Lista de pedido'
        verbose_name_plural = 'Listas de pedidos'
        ordering = ['-atualizado_em']

    def __str__(self):
        return self.nome or f'Lista #{self.pk}'


class ItemListaPedido(models.Model):
    """Item de uma lista de pedido (carrinho)."""
    lista = models.ForeignKey(
        ListaPedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.CASCADE,
        related_name='itens_lista'
    )
    quantidade = models.DecimalField('Quantidade', max_digits=12, decimal_places=3, default=1)
    preco_unitario = models.DecimalField('Preço unit.', max_digits=12, decimal_places=2)
    desconto = models.DecimalField('Desconto (R$)', max_digits=12, decimal_places=2, default=Decimal('0'))

    class Meta:
        verbose_name = 'Item da lista'
        verbose_name_plural = 'Itens da lista'
        unique_together = [['lista', 'produto']]

    @property
    def subtotal(self):
        return (self.quantidade * self.preco_unitario - self.desconto).quantize(Decimal('0.01'))
