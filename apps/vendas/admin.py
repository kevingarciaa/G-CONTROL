from django.contrib import admin
from .models import Venda, ItemVenda, ListaPedido, ItemListaPedido


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'empresa', 'cliente', 'vendedor', 'total', 'forma_pagamento', 'criado_em')
    list_filter = ('empresa', 'criado_em')
    search_fields = ('numero', 'cliente__nome')
    inlines = [ItemVendaInline]
    readonly_fields = ('numero', 'total')


class ItemListaPedidoInline(admin.TabularInline):
    model = ItemListaPedido
    extra = 0


@admin.register(ListaPedido)
class ListaPedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'empresa', 'cliente', 'vendedor', 'finalizada', 'atualizado_em')
    list_filter = ('empresa', 'finalizada')
    inlines = [ItemListaPedidoInline]
