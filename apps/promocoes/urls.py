from django.urls import path
from . import views

app_name = 'promocoes'

urlpatterns = [
    path('formas-pagamento/', views.formas_lista, name='formas'),
    path('formas-pagamento/nova/', views.forma_criar, name='forma_criar'),
    path('formas-pagamento/<int:pk>/editar/', views.forma_editar, name='forma_editar'),
    path('formas-pagamento/<int:pk>/excluir/', views.forma_excluir, name='forma_excluir'),
]
