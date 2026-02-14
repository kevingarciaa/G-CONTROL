from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo', 'empresa', 'is_staff')
    list_filter = ('tipo', 'empresa', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('GControl', {'fields': ('empresa', 'tipo', 'cpf', 'telefone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('GControl', {'fields': ('empresa', 'tipo', 'cpf', 'telefone')}),
    )
