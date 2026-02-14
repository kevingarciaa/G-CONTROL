from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms import LoginForm


class GControlLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class GControlLogoutView(LogoutView):
    next_page = 'login'
    http_method_names = ['get', 'post', 'head', 'options']

    def get(self, request, *args, **kwargs):
        """Permite GET para redirect('logout') e links diretos."""
        return self.post(request, *args, **kwargs)


@login_required
def home(request):
    """Redireciona para o dashboard de pedidos."""
    return redirect('pedidos:dashboard')
