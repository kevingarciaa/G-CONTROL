"""
Context processor para injetar a empresa do usuário logado nos templates.
"""
def empresa_atual(request):
    if request.user.is_authenticated and hasattr(request.user, 'empresa'):
        return {'empresa_atual': request.user.empresa}
    return {'empresa_atual': None}
