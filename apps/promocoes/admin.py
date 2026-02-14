from django.contrib import admin
from .models import RegraDesconto, FormaPagamento


@admin.register(RegraDesconto)
class RegraDescontoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'valor', 'valor_minimo_pedido', 'empresa', 'ativo', 'data_inicio', 'data_fim')
    list_filter = ('empresa', 'tipo', 'ativo')
    search_fields = ('nome',)


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'taxa_percentual', 'empresa', 'ativo')
    list_filter = ('empresa', 'ativo')
