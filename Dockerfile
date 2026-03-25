FROM python:3.14-slim AS base
# Metadados
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1
# Dependências mínimas para rodar binários
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates libc6 libgcc1 libstdc++6 \
    && rm -rf /var/lib/apt/lists/*
# Criar usuário 1000:1000
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -m -s /bin/bash app
# permissão para o diretório de trabalho
RUN mkdir -p /app && chown app:app /app
# definir o diretório de trabalho
WORKDIR /app
# INSTALAÇÃO DO UV (binário oficial, método fixo)
RUN curl -L "https://releases.astral.sh/github/uv/releases/download/0.11.1/uv-x86_64-unknown-linux-gnu.tar.gz" \
    -o /tmp/uv.tar.gz && \
    tar -xzf /tmp/uv.tar.gz -C /usr/local/bin --strip-components=1 && \
    rm /tmp/uv.tar.gz && \
    chmod +x /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uvx 
# Mudar para usuário não-root
USER app
# Copiar arquivos da aplicação 
COPY --chown=app:app pyproject.toml uv.lock ./
COPY --chown=app:app . .
# Instalar dependências
RUN uv sync --frozen --no-cache
# porta do container
EXPOSE 8000
# Entrypoint with deploy script
ENTRYPOINT ["bash", "entrypoint.sh"]
