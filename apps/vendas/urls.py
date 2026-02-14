from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('pdv/', views.pdv, name='pdv'),
    path('pdv/nova-lista/', views.lista_pedido_criar, name='lista_criar'),
    path('pdv/item/adicionar/', views.item_adicionar, name='item_adicionar'),
    path('pdv/item/<int:item_id>/remover/', views.item_remover, name='item_remover'),
    path('pdv/item/<int:item_id>/alterar-qtd/', views.item_alterar_qtd, name='item_alterar_qtd'),
    path('pdv/resumo/', views.resumo_checkout, name='resumo_checkout'),
    path('pdv/finalizar/', views.finalizar_venda, name='finalizar_venda'),
    path('pdv/item/<int:item_id>/desconto/', views.aplicar_desconto_item, name='desconto_item'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vendas/', views.vendas_lista, name='lista'),
    path('api/buscar-codigo-barras/', views.buscar_codigo_barras, name='buscar_codigo_barras'),
]
