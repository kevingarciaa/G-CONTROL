from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('metas/', views.metas_dashboard, name='metas_dashboard'),
    path('metas/definir/', views.metas_configurar, name='metas_configurar'),
    path('setores/', views.setores_lista, name='setores_lista'),
    path('setores/novo/', views.setor_criar, name='setor_criar'),
    path('setores/<int:pk>/editar/', views.setor_editar, name='setor_editar'),
    path('setores/<int:pk>/excluir/', views.setor_excluir, name='setor_excluir'),
    path('pedidos/', views.pedidos_lista, name='pedidos_lista'),
    path('pedidos/acompanhamento/', views.pedidos_acompanhamento, name='pedidos_acompanhamento'),
    path('pedidos/novo/', views.pedido_criar, name='pedido_criar'),
    path('pedidos/novo/item/adicionar/', views.pedido_rascunho_item_adicionar, name='pedido_rascunho_item_adicionar'),
    path('pedidos/novo/item/<int:indice>/remover/', views.pedido_rascunho_item_remover, name='pedido_rascunho_item_remover'),
    path('pedidos/<int:pk>/', views.pedido_acompanhar, name='pedido_acompanhar'),
    path('pedidos/<int:pk>/editar/', views.pedido_editar, name='pedido_editar'),
    path('pedidos/<int:pk>/excluir/', views.pedido_excluir, name='pedido_excluir'),
    path('pedidos/<int:pk>/mover-setor/', views.pedido_mover_setor, name='pedido_mover_setor'),
    path('pedidos/<int:pk>/item/adicionar/', views.pedido_item_adicionar, name='pedido_item_adicionar'),
    path('pedidos/<int:pk>/item/<int:item_pk>/remover/', views.pedido_item_remover, name='pedido_item_remover'),
    path('pedidos/<int:pk>/item/<int:item_pk>/alterar-qtd/', views.pedido_item_alterar_qtd, name='pedido_item_alterar_qtd'),
]
