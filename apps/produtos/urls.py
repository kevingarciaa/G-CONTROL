from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('produtos/', views.lista, name='lista'),
    path('produtos/estoque/', views.estoque, name='estoque'),
    path('produtos/estoque/exportar-excel/', views.estoque_exportar_excel, name='estoque_exportar_excel'),
    path('produtos/<int:pk>/estoque/ajustar/', views.estoque_ajustar, name='estoque_ajustar'),
    path('produtos/novo/', views.produto_criar, name='criar'),
    path('produtos/<int:pk>/editar/', views.produto_editar, name='editar'),
    path('produtos/<int:pk>/excluir/', views.produto_excluir, name='excluir'),
    path('produtos/excluir-varios/', views.produto_excluir_varios, name='excluir_varios'),
]
