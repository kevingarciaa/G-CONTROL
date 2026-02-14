"""
Produtos: cadastro com código de barras e estoque.
"""
from django.db import models


class Produto(models.Model):
    """Produto com código de barras e estoque."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='produtos'
    )
    nome = models.CharField('Nome', max_length=200)
    codigo_barras = models.CharField('Código de barras', max_length=100, blank=True, db_index=True)
    referencia_pedido = models.CharField('Referência ao pedido', max_length=200, blank=True)
    referencia_cliente = models.CharField('Referência ao cliente', max_length=200, blank=True)
    # Cálculo tecido: gramas/metro × valor do tecido = valor por peça
    gramas_por_metro = models.DecimalField('Gramas/metro (g)', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_tecido = models.DecimalField('Valor do tecido (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    # Cálculos: quantidade × valor unitário = valor por peça
    quantidade_estamparia = models.DecimalField('Qtd. estamparia', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_unitario_estamparia = models.DecimalField('Valor unit. estamparia (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    quantidade_acabamento = models.DecimalField('Qtd. acabamento', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_unitario_acabamento = models.DecimalField('Valor unit. acabamento (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    quantidade_aviamentos = models.DecimalField('Qtd. aviamentos', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_unitario_aviamentos = models.DecimalField('Valor unit. aviamentos (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    quantidade_costura = models.DecimalField('Qtd. costura', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_unitario_costura = models.DecimalField('Valor unit. costura (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    quantidade_outros = models.DecimalField('Qtd. outros', max_digits=12, decimal_places=4, default=0, blank=True)
    valor_unitario_outros = models.DecimalField('Valor unit. outros (R$)', max_digits=12, decimal_places=2, default=0, blank=True)
    preco_venda = models.DecimalField('Preço de venda', max_digits=12, decimal_places=2, default=0)
    preco_custo = models.DecimalField('Preço de custo', max_digits=12, decimal_places=2, default=0, blank=True)
    estoque_atual = models.DecimalField('Estoque atual', max_digits=12, decimal_places=3, default=0)
    unidade = models.CharField('Unidade', max_length=20, default='UN')  # UN, KG, L, CX, etc.
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
