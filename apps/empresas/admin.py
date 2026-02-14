from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nome_fantasia', 'cnpj', 'telefone', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'nome_fantasia', 'cnpj')
