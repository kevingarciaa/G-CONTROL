# GControl - Sistema de Gestão Comercial (Produto Kevin)

Sistema web para **controle de estoque** e **faturamento**, voltado para lojas, empresas, supermercados, barbearias, pizzarias etc. Desenvolvido em **Python** com **Django** e **Django Admin** como back-office.

## Funcionalidades

- **Dois tipos de login**
  - **Gestor (gerente/dono):** clientes, funcionários, produtos, relatórios e acesso ao Admin.
  - **Atendente:** cadastro de clientes e produtos.

- **Código de barras:** campo no cadastro de produtos.

- **Regras de desconto e promoções** (app Promoções + Admin).

- **Taxa por forma de pagamento** (ex.: taxa no cartão).

- **Aplicação desktop** (uso no navegador em ambiente local).

## Requisitos

- Python 3.10+
- Django 5+

## Instalação e execução

1. **Clone ou acesse a pasta do projeto e crie o ambiente virtual (opcional):**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Aplique as migrações:**
   ```bash
   python manage.py migrate
   ```

4. **Crie um superusuário (primeiro acesso ao Admin):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

6. **Acesse:**
   - **Sistema (login):** http://127.0.0.1:8000/
   - **Django Admin:** http://127.0.0.1:8000/admin/

## Configuração inicial no Admin

1. Acesse `/admin/` e faça login com o superusuário.

2. **Crie uma Empresa:**  
   Admin → Empresas → Adicionar (nome, CNPJ, etc.).

3. **Crie usuários da aplicação:**  
   Admin → Usuários → Adicionar:
   - Vincule à **Empresa**.
   - Defina o **Tipo:** **Gestor** ou **Atendente**.
   - Marque **Ativo** e defina a senha.

4. **Cadastre:** Produtos (com código de barras, se quiser), Clientes, Formas de pagamento e Regras de desconto.

5. Faça **logout** do Admin e entre em http://127.0.0.1:8000/ com um usuário **Gestor** ou **Atendente** para usar o sistema.

## Estrutura do projeto

```
G-Control/
├── gcontrol/           # Configurações do projeto
├── apps/
│   ├── empresas/       # Empresa (estabelecimento)
│   ├── usuarios/       # Usuário (Gestor / Atendente)
│   ├── produtos/       # Produto, código de barras, estoque
│   ├── clientes/       # Cliente
│   └── promocoes/      # Regra de desconto, Forma de pagamento (taxa)
├── templates/          # Templates base e por app
├── manage.py
└── requirements.txt
```

## Uso rápido

- **Produtos:** cadastre e edite produtos; use a lista e o controle de estoque para ajustes.
- **Gestor:** menu **Formas de pagamento** (gestor); **Admin** para cadastros avançados e relatórios.

## Observações

- **Código de barras:** campo disponível no cadastro de produtos.
- **Desktop:** use o sistema no navegador; por enquanto não há versão mobile específica.
