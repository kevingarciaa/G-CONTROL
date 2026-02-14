from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo_barras', 'preco_venda', 'estoque_atual', 'ativo')
    list_filter = ('empresa', 'ativo')
    search_fields = ('nome', 'codigo_barras')
    list_editable = ('ativo',)
