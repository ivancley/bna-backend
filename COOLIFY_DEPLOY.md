# 🚀 Deploy no Coolify - BNA Backend

Este guia explica como fazer o deploy do projeto BNA Backend no Coolify.

## 📋 Pré-requisitos

1. **Coolify** instalado e configurado
2. **Repositório Git** com o código
3. **Variáveis de ambiente** configuradas

## 🔧 Configuração das Variáveis de Ambiente

Configure as seguintes variáveis no painel do Coolify:

### Banco de Dados
```env
POSTGRES_DB=bna_db
POSTGRES_USER=bna_user
POSTGRES_PASSWORD=sua_senha_super_secreta_aqui
```

### JWT
```env
JWT_SECRET_KEY=sua_chave_jwt_super_secreta_aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### SMTP (Email)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app_gmail
SMTP_FRONTEND_URL=https://seu-frontend.com
```

### OpenAI
```env
OPENAI_API_KEY=sua_chave_openai_aqui
EMBED_MODEL=text-embedding-ada-002
```

## 🐳 Configuração do Docker Compose

O projeto está configurado para usar o `docker-compose.yml` otimizado para produção.

### Serviços Incluídos:

1. **PostgreSQL** com pgvector (banco principal)
2. **Redis** (cache e broker do Celery)
3. **FastAPI App** (aplicação principal)
4. **Celery Worker** (processamento de tarefas)
5. **Flower** (monitoramento - opcional)

## 📦 Deploy no Coolify

### Passo 1: Criar Nova Aplicação
1. Acesse o painel do Coolify
2. Clique em "New Application"
3. Selecione "Docker Compose"

### Passo 2: Configurar Repositório
1. Cole a URL do seu repositório Git
2. Configure a branch (geralmente `main`)

### Passo 3: Configurar Variáveis
1. Adicione todas as variáveis de ambiente listadas acima
2. **IMPORTANTE**: Configure senhas seguras para produção

### Passo 4: Configurar Volumes
Configure volumes persistentes para:
- `postgres_data` - Dados do PostgreSQL
- `redis_data` - Dados do Redis

### Passo 5: Deploy
1. Clique em "Deploy"
2. Aguarde o build e inicialização dos containers
3. Verifique os logs para garantir que tudo está funcionando

## 🔍 Verificação do Deploy

### Health Checks
- **FastAPI**: `http://seu-dominio:8000/health`
- **Flower**: `http://seu-dominio:5555` (se habilitado)

### Logs Importantes
- Verifique se as migrations foram executadas
- Confirme que o Celery Worker está conectado
- Teste uma requisição para a API

## 🛠️ Comandos Úteis

### Para desenvolvimento local:
```bash
# Subir todos os serviços
docker-compose up -d

# Subir com monitoramento (Flower)
docker-compose --profile monitoring up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Para produção:
```bash
# Build das imagens
docker-compose build

# Subir em produção
docker-compose up -d

# Verificar status
docker-compose ps
```

## 🔒 Segurança

### Configurações Aplicadas:
- ✅ Usuários não-root nos containers
- ✅ Imagens slim para reduzir superfície de ataque
- ✅ Variáveis de ambiente para configurações sensíveis
- ✅ Health checks para monitoramento
- ✅ Restart policies para alta disponibilidade

### Recomendações:
- Use senhas fortes para todas as variáveis
- Configure HTTPS no Coolify
- Monitore logs regularmente
- Mantenha as imagens atualizadas

## 🚨 Troubleshooting

### Problemas Comuns:

1. **❌ ERRO: "entrypoint.sh: not found" - Arquivo não encontrado durante build**
   
   **Causa:** O `.dockerignore` estava excluindo arquivos essenciais
   
   **Solução:**
   - ✅ **RESOLVIDO**: O `.dockerignore` foi corrigido
   - Use os arquivos Docker originais normalmente
   - Configure no Coolify para usar `docker-compose.yml`

2. **❌ ERRO: "Oops something is not okay"**
   
   **Possíveis causas e soluções:**
   - **Recursos insuficientes**: Aumente RAM/CPU do servidor Coolify
   - **Rede/DNS**: Verifique conectividade com Docker Hub
   - **Cache corrompido**: Limpe cache do Coolify
   - **Contexto de build grande**: Use o `.dockerignore` criado

3. **❌ Build muito lento ou falha por timeout**
   
   **Soluções:**
   - Use o `.dockerignore` otimizado para reduzir contexto
   - Configure build externo via GitHub Actions
   - Use imagens pré-buildadas se possível

4. **Migrations não executam**
   - Verifique se o PostgreSQL está acessível
   - Confirme as variáveis de banco

5. **Celery Worker não conecta**
   - Verifique se o Redis está funcionando
   - Confirme as variáveis REDIS_URL

6. **Chrome não funciona no Worker**
   - O Dockerfile.worker inclui todas as dependências necessárias
   - Verifique se não há problemas de permissão

7. **Health check falha**
   - Aguarde o tempo de inicialização (40s)
   - Verifique se a porta 8000 está exposta

### 🔧 Soluções Específicas para Coolify:

#### Opção 1: Usar arquivos originais (RECOMENDADO)
```bash
# No Coolify, configure para usar:
# Docker Compose File: docker-compose.yml
# Build Context: . (diretório raiz)
```

#### Opção 2: Build externo via GitHub Actions
```yaml
# .github/workflows/build.yml
name: Build and Push
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push
        run: |
          docker build -f Dockerfile -t your-registry/app:latest .
          docker push your-registry/app:latest
```

#### Opção 3: Configurações do Coolify
- **Build Context**: Use apenas o diretório necessário
- **Dockerfile**: Use `Dockerfile` (padrão)
- **Resources**: Aumente limites de CPU/RAM
- **Network**: Verifique conectividade com Docker Hub

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no Coolify
2. Teste localmente com `docker-compose up`
3. Confirme todas as variáveis de ambiente
4. Verifique se os volumes estão configurados corretamente
