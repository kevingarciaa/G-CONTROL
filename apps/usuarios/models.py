"""
Usuários do GControl: Gestor (admin da empresa) e Atendente (vendedor).
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """Usuário com perfil Gestor ou Atendente, vinculado a uma empresa."""

    class TipoUsuario(models.TextChoices):
        GESTOR = 'GESTOR', 'Gestor (Gerente/Dono)'
        ATENDENTE = 'ATENDENTE', 'Atendente/Vendedor'

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    tipo = models.CharField(
        'Tipo de usuário',
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.ATENDENTE
    )
    cpf = models.CharField('CPF', max_length=14, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_gestor(self):
        return self.tipo == self.TipoUsuario.GESTOR

    @property
    def is_atendente(self):
        return self.tipo == self.TipoUsuario.ATENDENTE

    def pode_gerenciar_funcionarios(self):
        return self.is_gestor

    def pode_ver_dashboard(self):
        return self.is_gestor

    def pode_ver_relatorios(self):
        return self.is_gestor
