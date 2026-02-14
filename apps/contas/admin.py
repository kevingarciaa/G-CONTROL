from django.contrib import admin
from .models import ContaPagar


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'data_vencimento', 'pago', 'data_pagamento', 'fornecedor', 'empresa']
    list_filter = ['pago', 'empresa']
    search_fields = ['descricao', 'observacao']
    date_hierarchy = 'data_vencimento'
