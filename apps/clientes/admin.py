from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf_cnpj', 'telefone', 'email', 'empresa', 'ativo')
    list_filter = ('empresa', 'ativo')
    search_fields = ('nome', 'cpf_cnpj', 'email')
