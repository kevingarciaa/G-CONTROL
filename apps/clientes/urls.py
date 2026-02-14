from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('clientes/', views.lista, name='lista'),
    path('clientes/novo/', views.cliente_criar, name='criar'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='editar'),
    path('clientes/<int:pk>/excluir/', views.cliente_excluir, name='excluir'),
]
