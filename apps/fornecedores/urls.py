from django.urls import path
from . import views

app_name = 'fornecedores'

urlpatterns = [
    path('fornecedores/', views.lista, name='lista'),
    path('fornecedores/novo/', views.fornecedor_criar, name='criar'),
    path('fornecedores/<int:pk>/editar/', views.fornecedor_editar, name='editar'),
    path('fornecedores/<int:pk>/excluir/', views.fornecedor_excluir, name='excluir'),
]
