"""
Setores (etapas de produção) e Pedidos.
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone


class Setor(models.Model):
    """Setor/etapa de produção (ex: Corte, Costura, Acabamento)."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='setores'
    )
    nome = models.CharField('Nome', max_length=80)
    ordem = models.PositiveSmallIntegerField('Ordem', default=0, help_text='Ordem de exibição')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['ordem', 'nome']
        unique_together = [['empresa', 'nome']]

    def __str__(self):
        return self.nome


STATUS_PEDIDO = [
    ('RASCUNHO', 'Rascunho'),
    ('EM_PRODUCAO', 'Em produção'),
    ('ENTREGUE', 'Entregue'),
    ('CANCELADO', 'Cancelado'),
]

PRAZO_CHOICES = [
    ('', '---------'),
    ('A_VISTA', 'À vista'),
    ('7_DIAS', '7 dias'),
    ('15_DIAS', '15 dias'),
    ('30_DIAS', '30 dias'),
    ('60_DIAS', '60 dias'),
    ('90_DIAS', '90 dias'),
    ('A_COMBINAR', 'A combinar'),
]


class Pedido(models.Model):
    """Pedido com acompanhamento por setor, prazos e valores."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos'
    )
    numero = models.PositiveIntegerField('Número', editable=False, default=0)
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_PEDIDO,
        default='RASCUNHO',
        db_index=True
    )
    setor_atual = models.ForeignKey(
        Setor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_no_setor',
        verbose_name='Setor atual'
    )
    data_entrada_setor = models.DateTimeField(
        'Entrada no setor em',
        null=True,
        blank=True,
        help_text='Quando o pedido entrou no setor atual (para alerta de parados)'
    )
    data_pedido = models.DateField('Data do pedido', default=timezone.localdate)
    data_prevista_entrega = models.DateField('Previsão de entrega (Setor)', null=True, blank=True)
    data_prevista_entrega_completo = models.DateField('Previsão de entrega (Pedido completo)', null=True, blank=True)
    data_entrega = models.DateField('Data de entrega', null=True, blank=True)
    valor_total = models.DecimalField(
        'Valor total (a receber)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    valor_custo = models.DecimalField(
        'Custo / a pagar',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    recebido = models.BooleanField('Valor recebido do cliente', default=False)
    pago = models.BooleanField('Custo pago', default=False)
    observacoes = models.TextField('Observações', blank=True)
    tamanhos = models.CharField(
        'Tamanhos',
        max_length=500,
        blank=True,
        help_text='Ex: Camiseta G, Calça 42, Short M, Vestido P...'
    )
    forma_pagamento = models.ForeignKey(
        'promocoes.FormaPagamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name='Forma de pagamento'
    )
    prazo = models.CharField(
        'Prazo',
        max_length=20,
        choices=PRAZO_CHOICES,
        blank=True,
        help_text='Determinação de prazo (pagamento ou entrega)'
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.numero}'

    def save(self, *args, **kwargs):
        if self.pk is None and self.empresa_id:
            ultimo = Pedido.objects.filter(empresa=self.empresa).order_by('-numero').first()
            self.numero = (ultimo.numero + 1) if ultimo else 1
        super().save(*args, **kwargs)

    @property
    def lucro(self):
        return (self.valor_total - self.valor_custo).quantize(Decimal('0.01'))

    @property
    def total_pecas(self):
        """Soma das quantidades de todos os itens do pedido."""
        from django.db.models import Sum
        r = self.itens.aggregate(s=Sum('quantidade'))['s']
        return int(r) if r is not None else 0

    @property
    def em_atraso(self):
        if self.status != 'EM_PRODUCAO' or not self.data_prevista_entrega:
            return False
        return self.data_prevista_entrega < timezone.localdate()

    def dias_no_setor_atual(self):
        """Quantidade de dias no setor atual (para alerta de parados)."""
        if not self.data_entrada_setor:
            return None
        delta = timezone.now() - self.data_entrada_setor
        return delta.days

    def recalcular_totais_dos_itens(self):
        """Atualiza valor_total e valor_custo com a soma dos itens do pedido."""
        from django.db.models import Sum, F
        agg = self.itens.aggregate(
            total=Sum(F('quantidade') * F('preco_unitario')),
            custo=Sum(F('quantidade') * F('preco_custo_unitario'))
        )
        self.valor_total = (agg['total'] or Decimal('0')).quantize(Decimal('0.01'))
        self.valor_custo = (agg['custo'] or Decimal('0')).quantize(Decimal('0.01'))
        self.save(update_fields=['valor_total', 'valor_custo'])


class ItemPedido(models.Model):
    """Item do pedido: produto, quantidade e preços (fixados no momento da inclusão)."""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.PROTECT,
        related_name='itens_pedido'
    )
    quantidade = models.DecimalField(
        'Quantidade',
        max_digits=12,
        decimal_places=3,
        default=1
    )
    preco_unitario = models.DecimalField(
        'Preço unit. (venda)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    preco_custo_unitario = models.DecimalField(
        'Custo unit.',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    tamanhos = models.CharField(
        'Tamanhos',
        max_length=500,
        blank=True,
        help_text='Tamanhos deste item (ex: G, 42)'
    )

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'
        unique_together = [['pedido', 'produto', 'tamanhos']]
        ordering = ['produto', 'tamanhos', 'id']

    def __str__(self):
        return f'{self.produto.nome} x {self.quantidade}'

    @property
    def subtotal(self):
        return (self.quantidade * self.preco_unitario).quantize(Decimal('0.01'))

    @property
    def custo_total(self):
        return (self.quantidade * self.preco_custo_unitario).quantize(Decimal('0.01'))


TIPO_META = [
    ('RECEBER', 'Meta a receber'),
    ('LUCRO', 'Meta de lucro'),
    ('PRODUCAO', 'Meta de produção'),
]

PERIODO_META_CHOICES = [
    (None, 'Todo o período'),
    (30, 'Mensal (30 dias)'),
    (60, '60 dias'),
    (90, '90 dias'),
    (365, 'Anual (365 dias)'),
]


class MetaValor(models.Model):
    """Meta de valor por tipo (a receber, lucro) para a empresa, com período opcional."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='metas_valor'
    )
    tipo = models.CharField(
        'Tipo',
        max_length=20,
        choices=TIPO_META
    )
    valor_meta = models.DecimalField(
        'Valor da meta (R$)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )
    periodo_dias = models.PositiveIntegerField(
        'Período (dias)',
        null=True,
        blank=True,
        help_text='Meta para os últimos N dias (ex.: 30 = mensal, 60 = 60 dias). Vazio = todo o período.'
    )
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Meta de valor'
        verbose_name_plural = 'Metas de valor'
        unique_together = [['empresa', 'tipo']]

    def __str__(self):
        if self.tipo == 'PRODUCAO':
            return f'{self.get_tipo_display()}: {self.valor_meta} peças'
        return f'{self.get_tipo_display()}: R$ {self.valor_meta}'

    def get_periodo_display(self):
        if self.periodo_dias is None:
            return 'Todo o período'
        for valor, label in PERIODO_META_CHOICES:
            if valor == self.periodo_dias:
                return label
        return f'{self.periodo_dias} dias'
