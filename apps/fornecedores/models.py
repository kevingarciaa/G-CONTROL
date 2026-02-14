"""
Fornecedores da empresa.
"""
from django.db import models


SEGMENTO_CHOICES = [
    ('', '---------'),
    ('ESTAMPARIA', 'Estamparia'),
    ('COSTURA', 'Costura'),
    ('BORDADO', 'Bordado'),
    ('ACABAMENTO', 'Acabamento'),
    ('TECIDO', 'Tecido'),
    ('AVIAMENTO', 'Aviamento'),
    ('LAVANDERIA', 'Lavanderia'),
]


class Fornecedor(models.Model):
    """Fornecedor (pessoa física ou jurídica) para compras."""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='fornecedores'
    )
    nome = models.CharField('Nome', max_length=200)
    segmento = models.CharField(
        'Segmento',
        max_length=20,
        choices=SEGMENTO_CHOICES,
        blank=True,
    )
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, blank=True)
    email = models.EmailField('E-mail', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    endereco = models.CharField('Endereço', max_length=300, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
