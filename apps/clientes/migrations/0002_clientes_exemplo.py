# Generated migration - Clientes de exemplo para visualização

from django.db import migrations


def criar_clientes_exemplo(apps, schema_editor):
    Empresa = apps.get_model('empresas', 'Empresa')
    Cliente = apps.get_model('clientes', 'Cliente')

    clientes_exemplo = [
        {'nome': 'Maria Silva Santos', 'cpf_cnpj': '123.456.789-00', 'email': 'maria.silva@email.com', 'telefone': '(11) 98765-4321', 'endereco': 'Rua das Flores, 123 - Centro'},
        {'nome': 'João Oliveira Costa', 'cpf_cnpj': '987.654.321-00', 'email': 'joao.oliveira@email.com', 'telefone': '(11) 91234-5678', 'endereco': 'Av. Brasil, 456 - Jardim'},
        {'nome': 'Ana Paula Ferreira', 'cpf_cnpj': '456.789.123-00', 'email': 'ana.ferreira@email.com', 'telefone': '(11) 99876-5432', 'endereco': 'Rua do Comércio, 789'},
        {'nome': 'Carlos Eduardo Souza', 'cpf_cnpj': '321.654.987-00', 'email': 'carlos.souza@email.com', 'telefone': '(11) 97654-3210', 'endereco': 'Rua Augusta, 100'},
        {'nome': 'Fernanda Lima Rocha', 'cpf_cnpj': '789.123.456-00', 'email': 'fernanda.rocha@email.com', 'telefone': '(11) 96543-2109', 'endereco': 'Alameda Santos, 200'},
        {'nome': 'Roberto Almeida Santos', 'cpf_cnpj': '147.258.369-00', 'email': 'roberto.almeida@email.com', 'telefone': '(11) 95432-1098', 'endereco': 'Rua Oscar Freire, 500'},
        {'nome': 'Patrícia Mendes Lima', 'cpf_cnpj': '369.258.147-00', 'email': 'patricia.mendes@email.com', 'telefone': '(11) 94321-0987', 'endereco': 'Av. Paulista, 1000'},
    ]

    for empresa in Empresa.objects.all():
        if not Cliente.objects.filter(empresa=empresa).exists():
            for dados in clientes_exemplo:
                Cliente.objects.create(empresa=empresa, **dados)


def remover_clientes_exemplo(apps, schema_editor):
    # Opcional: remover clientes de exemplo no rollback
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_clientes_exemplo, remover_clientes_exemplo),
    ]
