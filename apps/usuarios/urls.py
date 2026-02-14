from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.GControlLoginView.as_view(), name='login'),
    path('logout/', views.GControlLogoutView.as_view(), name='logout'),
]
