# Codecov - Configuração de Cobertura de Testes

Este documento explica como configurar o Codecov para receber automaticamente os relatórios de cobertura de testes do projeto.

## 🎯 O que é o Codecov?

O Codecov é uma plataforma que:
- Visualiza a cobertura de testes do seu código
- Mostra quais linhas/arquivos não têm testes
- Gera relatórios detalhados e gráficos de evolução
- Comenta automaticamente em Pull Requests com mudanças na cobertura

## 🔧 Configuração Inicial

### 1. Criar conta no Codecov

1. Acesse [codecov.io](https://codecov.io)
2. Faça login com sua conta do GitHub
3. Autorize o Codecov a acessar seus repositórios

### 2. Adicionar o repositório

1. No dashboard do Codecov, clique em **"Add Repository"**
2. Procure por `<seu-usuario>/<nome-repo>`
3. Ative o repositório

### 3. Obter o token do Codecov

**Para repositórios públicos**: O token é **opcional** (Codecov funciona sem ele)

**Para repositórios privados**: O token é **obrigatório**

#### Como obter o token:

1. No Codecov, acesse o repositório ativado
2. Clique em **Settings** → **General**
3. Copie o **Repository Upload Token**

### 4. Adicionar o token como secret no GitHub

**Apenas para repositórios privados**:

1. No GitHub, vá em: `Settings` → `Secrets and variables` → `Actions`
2. Clique em **"New repository secret"**
3. Nome: `CODECOV_TOKEN`
4. Valor: Cole o token copiado do Codecov
5. Clique em **"Add secret"**

## 📊 Workflow Configurado

O workflow `.github/workflows/tests.yml` já está configurado para enviar automaticamente os relatórios:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
    fail_ci_if_error: false
    token: ${{ secrets.CODECOV_TOKEN }}
```

### Parâmetros:

- **file**: Caminho do arquivo XML de cobertura gerado pelo pytest-cov
- **flags**: Tag para identificar diferentes tipos de testes
- **name**: Nome do upload (útil para múltiplas uploads)
- **fail_ci_if_error**: `false` = não falha o workflow se o upload falhar
- **token**: Token do Codecov (obrigatório para repos privados)

## 🚀 Como funciona

1. **Testes executam** → Gera `coverage.xml`
2. **Codecov action** → Faz upload do arquivo para Codecov
3. **Codecov processa** → Gera relatórios e gráficos
4. **Resultados disponíveis** → No site do Codecov e em PRs

## 📈 Visualizar Relatórios

### No Codecov.io

1. Acesse [codecov.io/gh/<seu-usuario>/<nome-repo>](https://codecov.io)
2. Veja:
   - Porcentagem total de cobertura
   - Arquivos com menor cobertura
   - Linhas não cobertas
   - Gráficos de evolução ao longo do tempo

### Em Pull Requests

O Codecov automaticamente comenta em PRs mostrando:
- Mudança na cobertura (↑ ou ↓)
- Arquivos modificados e sua cobertura
- Comparação com a branch base

## 🎨 Badge no README

O badge de cobertura já está configurado no README:

```markdown
![Codecov](https://codecov.io/gh/<seu-usuario>/<nome-repo>/branch/main/graph/badge.svg)
```

**Lembre-se de substituir**: `<seu-usuario>` e `<nome-repo>` pelos valores reais

Exemplo:
```markdown
![Codecov](https://codecov.io/gh/johndoe/crm-api/branch/main/graph/badge.svg)
```

## 🔒 Repositórios Públicos vs Privados

### Repositórios Públicos
- ✅ Token **opcional** (Codecov funciona sem ele)
- ✅ Relatórios públicos e acessíveis
- ✅ Badge funciona automaticamente

### Repositórios Privados
- ⚠️ Token **obrigatório** (adicionar como secret)
- 🔒 Relatórios privados (apenas membros do repo)
- 🔒 Badge requer token na URL ou configuração especial

## 📝 Arquivo de Configuração (Opcional)

Você pode criar um arquivo `.codecov.yml` na raiz do projeto para customizar:

```yaml
# .codecov.yml (exemplo)
coverage:
  precision: 2
  round: down
  range: "70...100"
  status:
    project:
      default:
        target: 80%
    patch:
      default:
        target: 80%

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false

ignore:
  - "*/tests/*"
  - "*/migrations/*"
  - "manage.py"
  - "*/admin.py"
```

### Configurações úteis:

- **target**: Meta de cobertura (ex: 80%)
- **ignore**: Arquivos/pastas a ignorar no cálculo
- **comment**: Personalizar comentários em PRs
- **precision**: Casas decimais na porcentagem

## 🎯 Metas de Cobertura

Você pode definir metas de cobertura no Codecov:

1. No Codecov, vá em **Settings** → **General**
2. Configure **Target Coverage**
3. O Codecov marcará o check como ❌ se a cobertura cair abaixo da meta

## 🔍 Analisar Cobertura Localmente

Antes de fazer push, você pode verificar a cobertura localmente:

```bash
# Executar testes com cobertura
uv run coverage run --source='clientes,crm_api' -m pytest clientes/tests -v

# Ver relatório no terminal
uv run coverage report -m

# Gerar relatório HTML interativo
uv run coverage html

# Abrir no navegador (Linux/WSL)
xdg-open htmlcov/index.html
```

## 🆘 Troubleshooting

### Upload falha com "401 Unauthorized"
- Verifique se o `CODECOV_TOKEN` está configurado corretamente nos secrets
- Confirme que copiou o token completo (sem espaços)

### Badge não aparece
- Aguarde o primeiro upload de cobertura
- Verifique se o nome do repositório no badge está correto
- Para repos privados, use um token específico na URL do badge

### Cobertura mostra 0% ou valor errado
- Verifique se o arquivo `coverage.xml` está sendo gerado
- Confirme que o `--source` do coverage inclui os módulos corretos
- Verifique se o `.codecov.yml` não está ignorando arquivos importantes

### Codecov não comenta em PRs
- Em Settings → General → Pull Request Comments → Marque "Enable"
- Verifique se o Codecov app tem permissão no GitHub

## 📚 Recursos Adicionais

- [Documentação oficial do Codecov](https://docs.codecov.com)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [Configuração do .codecov.yml](https://docs.codecov.com/docs/codecov-yaml)

## ✅ Checklist de Configuração

- [ ] Conta criada no Codecov
- [ ] Repositório ativado no Codecov
- [ ] Token adicionado como secret (se repo privado)
- [ ] Workflow executado com sucesso
- [ ] Badge atualizado no README com usuário/repo corretos
- [ ] Primeiro relatório visualizado no Codecov
- [ ] (Opcional) `.codecov.yml` configurado
