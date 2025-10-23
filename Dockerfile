FROM python:3.13-slim

# Define diretório de trabalho
WORKDIR /app

# Variáveis de ambiente Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    netcat-openbsd \
    redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria entrypoint diretamente no Dockerfile
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo 'echo "🚀 Iniciando BNA Backend..."' >> /entrypoint.sh && \
    echo 'echo "📋 Variáveis de ambiente:"' >> /entrypoint.sh && \
    echo 'echo "  POSTGRES_DB: ${POSTGRES_DB:-bna_db}"' >> /entrypoint.sh && \
    echo 'echo "  POSTGRES_USER: ${POSTGRES_USER:-bna_user}"' >> /entrypoint.sh && \
    echo 'echo "  JWT_SECRET_KEY: ${JWT_SECRET_KEY:+[CONFIGURADO]}"' >> /entrypoint.sh && \
    echo 'echo "  SMTP_HOST: ${SMTP_HOST:+[CONFIGURADO]}"' >> /entrypoint.sh && \
    echo 'echo "  OPENAI_API_KEY: ${OPENAI_API_KEY:+[CONFIGURADO]}"' >> /entrypoint.sh && \
    echo 'echo "🔄 Aguardando PostgreSQL estar pronto..."' >> /entrypoint.sh && \
    echo 'until PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U ${POSTGRES_USER:-bna_user} -d ${POSTGRES_DB:-bna_db} -c "\\q" 2>/dev/null; do' >> /entrypoint.sh && \
    echo '  echo "⏳ PostgreSQL ainda não está pronto - aguardando..."' >> /entrypoint.sh && \
    echo '  sleep 2' >> /entrypoint.sh && \
    echo 'done' >> /entrypoint.sh && \
    echo 'echo "✅ PostgreSQL está pronto!"' >> /entrypoint.sh && \
    echo 'echo "🔄 Aguardando Redis estar pronto..."' >> /entrypoint.sh && \
    echo 'until redis-cli -h redis ping 2>/dev/null | grep -q PONG; do' >> /entrypoint.sh && \
    echo '  echo "⏳ Redis ainda não está pronto - aguardando..."' >> /entrypoint.sh && \
    echo '  sleep 2' >> /entrypoint.sh && \
    echo 'done' >> /entrypoint.sh && \
    echo 'echo "✅ Redis está pronto!"' >> /entrypoint.sh && \
    echo 'echo "🔄 Executando migrations do Alembic..."' >> /entrypoint.sh && \
    echo 'alembic upgrade head || echo "⚠️  Erro nas migrations, continuando..."' >> /entrypoint.sh && \
    echo 'echo "✅ Migrations processadas!"' >> /entrypoint.sh && \
    echo 'echo "🚀 Iniciando aplicação FastAPI..."' >> /entrypoint.sh && \
    echo 'echo "📡 Servidor será iniciado em: http://0.0.0.0:8000"' >> /entrypoint.sh && \
    echo 'echo "📚 Documentação disponível em: http://0.0.0.0:8000/docs"' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Cria usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expõe porta do FastAPI
EXPOSE 8000

# Usa entrypoint para rodar migrations antes do app
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão: inicia FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]