from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from .models import Setor, Pedido, ItemPedido, MetaValor


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'ordem', 'ativo')
    list_filter = ('empresa', 'ativo')
    search_fields = ('nome',)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    raw_id_fields = ('produto',)


class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'numero', 'cliente', 'status', 'setor_atual', 'data_pedido',
        'data_prevista_entrega', 'valor_total', 'valor_custo', 'recebido', 'pago'
    )
    list_filter = ('empresa', 'status', 'recebido', 'pago')
    search_fields = ('numero', 'cliente__nome', 'observacoes')
    date_hierarchy = 'data_pedido'
    raw_id_fields = ('cliente',)
    inlines = [ItemPedidoInline]


try:
    admin.site.unregister(Pedido)
except NotRegistered:
    pass
admin.site.register(Pedido, PedidoAdmin)


@admin.register(MetaValor)
class MetaValorAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'tipo', 'valor_meta', 'atualizado_em')
    list_filter = ('empresa', 'tipo')
