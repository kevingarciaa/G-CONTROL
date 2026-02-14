"""
Modelo de Empresa - cada comércio (loja, supermercado, barbearia, etc.)
"""
from django.db import models


class Empresa(models.Model):
    """Empresa/estabelecimento que usa o GControl."""
    nome = models.CharField('Nome', max_length=200)
    nome_fantasia = models.CharField('Nome fantasia', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
    endereco = models.CharField('Endereço', max_length=300, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']

    def __str__(self):
        return self.nome_fantasia or self.nome
