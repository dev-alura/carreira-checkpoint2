# GitHub Container Registry - Configuração

Este documento explica como está configurado o GitHub Actions para publicar automaticamente as imagens Docker no GitHub Container Registry (ghcr.io).

## 🔄 Processo Automático

O workflow `.github/workflows/tests.yml` realiza automaticamente:

1. **Executa os testes** com cobertura
2. **Constrói a imagem Docker** (apenas se os testes passarem)
3. **Publica no GitHub Container Registry** (apenas em push, não em PRs)

### Triggers

- **Push** nas branches `main` ou `develop` → Roda testes + Build + Push da imagem
- **Pull Request** → Apenas roda os testes (não faz build da imagem)

## 🏷️ Tags Geradas

O workflow gera automaticamente as seguintes tags:

- `ghcr.io/<seu-usuario>/<nome-repo>:<branch>` - Tag da branch (ex: `main`, `develop`)
- `ghcr.io/<seu-usuario>/<nome-repo>:<branch>-<sha>` - Tag com SHA do commit
- `ghcr.io/<seu-usuario>/<nome-repo>:latest` - Tag latest (apenas para branch default)

### Exemplo de tags geradas:
```
ghcr.io/seu-usuario/crm-api:main
ghcr.io/seu-usuario/crm-api:main-abc1234
ghcr.io/seu-usuario/crm-api:latest
```

## 📦 Como Usar a Imagem

### 1. Tornar o pacote público (recomendado para projetos open source)

1. Acesse: `https://github.com/<seu-usuario>/<nome-repo>/pkgs/container/<nome-repo>`
2. Clique em "Package settings"
3. Role até "Danger Zone" e clique em "Change visibility"
4. Selecione "Public" e confirme

### 2. Baixar e executar a imagem

```bash
# Baixar a imagem
docker pull ghcr.io/<seu-usuario>/<nome-repo>:latest

# Executar com variáveis de ambiente necessárias
docker run -it -p 8000:8000 \
  -e DEBUG="False" \
  -e SECRET_KEY="sua-secret-key-aqui" \
  -e ALLOWED_HOSTS="*" \
  -e CORS_ALLOWED_ORIGINS_ENV='["http://localhost:8000"]' \
  -e ENVIROMENT="PROD" \
  -e DB_NAME="crmapi" \
  -e DB_USER="postgres" \
  -e DB_PASS="postgres" \
  -e DB_HOST="postgres" \
  -e DB_PORT="5432" \
  ghcr.io/<seu-usuario>/<nome-repo>:latest
```

### 3. Usar com Docker Compose

Edite o `docker-compose.yml` e substitua o build pela imagem:

```yaml
services:
  web:
    # image: ghcr.io/<seu-usuario>/<nome-repo>:latest  # Descomente para usar do registry
    build: .  # Comente esta linha ao usar do registry
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
      # ... outras variáveis
```

## 🔐 Autenticação (para imagens privadas)

Se o pacote for privado, você precisa autenticar:

```bash
# 1. Criar um Personal Access Token (PAT) no GitHub
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# Marque o escopo: read:packages

# 2. Fazer login
echo "SEU_TOKEN_AQUI" | docker login ghcr.io -u SEU_USUARIO --password-stdin

# 3. Agora pode fazer pull
docker pull ghcr.io/seu-usuario/crm-api:latest
```

## 🛠️ Integração CI/CD

O workflow usa:

- **Docker Buildx** - Para builds multi-plataforma e cache eficiente
- **GitHub Actions Cache** - Cache de layers do Docker (`cache-from`/`cache-to`)
- **GITHUB_TOKEN** - Autenticação automática (não precisa configurar secrets)

### Permissões Necessárias

O workflow já está configurado com as permissões corretas:

```yaml
permissions:
  contents: read
  packages: write
```

## 🔍 Verificar Publicação

Após o push, você pode verificar:

1. **Actions tab** no GitHub → Ver o workflow rodando
2. **Packages** na página principal do repo → Ver as imagens publicadas
3. **Releases** → As tags/versões disponíveis

## 📝 Observações

- As imagens são construídas **apenas após os testes passarem**
- O cache do Docker é preservado entre builds (acelera builds subsequentes)
- Cada push gera uma nova imagem com tag única (SHA do commit)
- A tag `latest` é atualizada apenas na branch default (main)

## 🆘 Troubleshooting

### Erro: "permission denied"
- Verifique se o repositório tem permissão para criar packages
- Em Settings → Actions → General → Workflow permissions → Marque "Read and write permissions"

### Imagem não aparece
- Verifique se o workflow completou com sucesso
- O job `build-and-push` só roda em `push` (não em PRs)
- Verifique os logs do workflow

### Não consigo fazer pull
- Verifique se a imagem é pública ou se você está autenticado
- Confirme que o nome da imagem está correto (case-sensitive)
