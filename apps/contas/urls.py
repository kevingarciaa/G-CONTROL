from django.urls import path
from . import views

app_name = 'contas'

urlpatterns = [
    path('contas-a-pagar/', views.lista, name='lista'),
    path('contas-a-pagar/nova/', views.conta_criar, name='criar'),
    path('contas-a-pagar/<int:pk>/editar/', views.conta_editar, name='editar'),
    path('contas-a-pagar/<int:pk>/excluir/', views.conta_excluir, name='excluir'),
    path('contas-a-pagar/<int:pk>/marcar-pago/', views.conta_marcar_pago, name='marcar_pago'),
]
