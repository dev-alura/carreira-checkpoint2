![Python](https://img.shields.io/badge/python-3.14-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/django-5.1-green?logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/djangorestframework-3.15-red?logo=django&logoColor=white)
![DevContainer](https://img.shields.io/badge/devcontainer-enabled-blue?logo=visualstudiocode&logoColor=white)

# Projeto: Gerenciador de Relacionamento com Clientes

Você chegou a um novo momento da sua jornada! Agora é hora de aplicar, de forma integrada, os conhecimentos que vem construindo até aqui em um desafio mais completo e realista, com foco na atuação de pessoas desenvolvedoras back-end em times profissionais.  

Neste projeto, você será responsável por desenvolver um sistema de CRM (Customer Relationship Management), voltado para o gerenciamento de clientes e suas interações. A proposta é simular o dia a dia de desenvolvimento de um sistema real, desde a modelagem dos dados até o deploy da aplicação em um ambiente pronto para produção.  

## Infraesturura e montagem do ambiente 
 - Desenvolvimento 
   - [Devcontainer Microsoft](https://code.visualstudio.com/docs/devcontainers/containers)
   - uv / ruff - gerenciadores de pacote e lint
   - python 3.14 
   - Siga o exemplo do .env_examples e coloque o ENVIROMENT em test para não usar o postgres 
   - Execute: ./entrypoint_dev.sh assim que carregar o devcontainer 
   - Projeto tem Documentação do projeto [Swagger/Redocs](http://localhost:8000/swagger)

## Etapas:

 - [x] Criar modelos de dados e APIs com Django e Django REST Framework.
 - [ ] Organizar o projeto de forma escalável, com boas práticas de arquitetura.
 - [x] Implementar autenticação com tokens e proteger os endpoints da aplicação.
 - [ ] Construir testes automatizados (unitários e de integração), 
    - [ ] Utilizando fixtures para simular cenários reais.
 - [x] Desenvolver funcionalidades com filtros, busca e ordenação para melhorar a experiência da API.
 - [x] Conteinerizar a aplicação com Docker
    - [x] Deixar o sistema pronto para ser executado em qualquer ambiente.

Ao final desse desafio, você terá uma aplicação sólida, estruturada de forma profissional, e que pode (e deve!) ser incluída no seu portfólio para demonstrar sua evolução na carreira de desenvolvimento com Python.  

## Roteiro 
Passos exigidos pelo desafio da entrega serão anotados aqui !

### Estrutura inicial e cadastro de clientes

 - [x] Criar o projeto base e o módulo responsável pelo cadastro de clientes.
 - [x] Definir o modelo de dados com os campos necessários.
 - [x] Garantir que as informações possam ser armazenadas e recuperadas pela API.
 - [x] Expor dois endpoints públicos: um para cadastrar clientes e outro para listá-los.
 - [x] Garantir que a data de criação seja preenchida automaticamente e que o email não se repita.

### Implementando autenticação segura

 - [x] Criar um mecanismo de autenticação via TokenAuth ou JWT com expiração.
 - [x] Desenvolver um endpoint para login e geração de token.
 - [x] Configurar o CORS para permitir apenas origens autorizadas acessarem a API.
 - [x] Restringir o acesso aos endpoints de cliente, exigindo autenticação.
 - [x] Garantir que apenas usuários autenticados consigam listar e cadastrar.  
 - [x] Garantir que apenas cadastrar usuarioas no sitemas pelo endpoint.

### Consultando clientes por filtros e parâmetros

 - [x] Adicionar suporte a parâmetros de busca (query parameters) no endpoint de listagem de clientes.
 - [x] Permitir que a listagem retorne apenas os clientes que correspondam ao nome, email ou telefone informados.
 - [x] Garantir que o filtro seja case-insensitive e funcione mesmo com buscas parciais.
 - [x] Manter a necessidade de autenticação para acessar esse recurso.

 ### Adicionando notas e histórico para cada cliente

 - [x] Criar um novo modelo de Nota que esteja relacionado a um cliente.
 - [x] Cada nota deve conter um texto descritivo e uma data de criação automática.
 - [x] Criar os endpoints para:
   - [x] Adicionar uma nova nota a um cliente existente.
   - [x] Listar todas as notas vinculadas a um cliente específico.
 - [x] Garantir que apenas usuários autenticados possam realizar essas ações.

### Implementando permissões de acesso

 - [x] administrador: com acesso total ao sistema
 - [x] vendedor: com acesso restrito, apenas para cadastro e consulta de clientes e notas

 - [x] Definir perfis de usuário ou grupos de permissão (administrador e vendedor, no mínimo).
 - [x] Restringir o acesso a determinados endpoints com base no tipo de usuário autenticado.
 - [x] Garantir que vendedores só possam visualizar ou editar registros dos seus próprios clientes e notas, vinculando cada cliente a um responsável.
 - [x] Garantir que administradores tenham acesso completo a todos os recursos.
 - [x] Escrever testes cobrindo cenários de ownership, validando que:
 - [x] Vendedores não conseguem acessar clientes ou notas de outros vendedores.
 - [x] Administradores conseguem listar e editar qualquer cliente ou nota.

### Criando testes automatizados

 - [x] Cadastro de clientes (dados válidos e inválidos, emails duplicados).
 - [x] Autenticação de usuários (login, tokens inválidos e acesso a rotas protegidas).
 - [x] Criação e consulta de interações (notas associadas a clientes).
 - [x] Verificação das permissões de acesso (administrador x vendedor).
 - [x] Filtros de listagem (busca por nome, email ou telefone, case-insensitive).

### Conteinerizando sua aplicação com Docker

 - [x] Criar um arquivo Dockerfile para empacotar a aplicação Django.
 - [x] Criar um arquivo docker-compose.yml para orquestrar a aplicação e o banco de dados PostgreSQL.
 - [x] Garantir que o container esteja exposto na porta correta e conectado ao banco.
 - [x] Permitir que o container seja iniciado com um único comando, como docker-compose up.
 - [x] Configurar o container para rodar migrações automaticamente na inicialização.
 - [x] Criar um workflow de GitHub Actions que:
   - [x] Rode os testes automatizados a cada push/pull request.
   - [x] Gere relatório de cobertura de testes.
   - [x] Construa a imagem Docker da aplicação.
 - [x] Utilizar um .dockerignore para evitar copiar arquivos desnecessários para dentro da imagem.

## Comandos
```
# Cobertura
uv run coverage run --source='clientes,crm_api' -m pytest clientes/tests -v

docker run -it -p 8000:8000 -e DEBUG="False" -e CORS_ALLOWED_ORIGINS_ENV='["http://localhost:8000"]' -e SECRET_KEY="django-insecure-p_%^w*s2z3&toghdkwig=a)7#&0p-%r(76yf(mhv#b-gnxg!=*" -e ALLOWED_HOSTS="*" crm-api:latest
```