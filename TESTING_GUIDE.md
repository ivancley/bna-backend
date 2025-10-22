# 🧪 Guia de Testes - BNA Backend

Este guia explica como testar o projeto BNA Backend em diferentes ambientes.

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- `curl` instalado
- `jq` instalado (opcional, para formatação JSON)

## 🏠 Teste Local (Desenvolvimento)

### Teste Automatizado

```bash
# Executar teste completo
./test-local.sh
```

Este script irá:
- ✅ Verificar se Docker está rodando
- ✅ Fazer build das imagens
- ✅ Subir todos os serviços
- ✅ Testar conectividade de cada serviço
- ✅ Verificar endpoints da API
- ✅ Mostrar logs dos serviços
- ✅ Gerar relatório de status

### Teste Manual Passo a Passo

```bash
# 1. Subir os serviços
docker-compose up -d

# 2. Aguardar inicialização (30-60 segundos)
sleep 30

# 3. Testar health check
curl http://localhost:8000/health

# 4. Testar documentação
curl http://localhost:8000/docs

# 5. Verificar logs
docker-compose logs -f

# 6. Verificar status dos containers
docker-compose ps

# 7. Parar serviços
docker-compose down
```

### URLs para Teste Local

- **API Health**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Flower (Celery)**: http://localhost:5555 (se habilitado)

## 🚀 Teste em Produção (Coolify)

### Teste Automatizado

```bash
# Teste básico
./test-production.sh https://seu-dominio.com

# Exemplo com IP
./test-production.sh http://192.168.1.100:8000
```

Este script irá:
- ✅ Testar conectividade básica
- ✅ Verificar endpoints essenciais
- ✅ Testar performance e latência
- ✅ Verificar headers de segurança
- ✅ Fazer testes de stress
- ✅ Gerar relatório completo

### Teste Manual em Produção

```bash
# 1. Teste básico de conectividade
curl https://seu-dominio.com/health

# 2. Teste de documentação
curl https://seu-dominio.com/docs

# 3. Teste com verbose para debug
curl -v https://seu-dominio.com/health

# 4. Teste de headers
curl -I https://seu-dominio.com/health

# 5. Teste de timeout
timeout 10 curl https://seu-dominio.com/health
```

## 🔍 Verificações Específicas

### 1. Health Check

```bash
# Deve retornar status 200 e JSON com timestamp
curl https://seu-dominio.com/health

# Resposta esperada:
# {"status": "healthy", "timestamp": "2024-01-01T12:00:00"}
```

### 2. Banco de Dados

```bash
# Verificar se migrations foram executadas
docker-compose exec app alembic current

# Verificar conexão com banco
docker-compose exec app psql $DATABASE_URL -c "SELECT 1;"
```

### 3. Redis

```bash
# Verificar conexão Redis
docker-compose exec redis redis-cli ping

# Deve retornar: PONG
```

### 4. Celery Worker

```bash
# Verificar worker ativo
docker-compose exec worker celery -A api.utils.celery_app inspect active

# Verificar queues
docker-compose exec worker celery -A api.utils.celery_app inspect stats
```

### 5. Endpoints da API

```bash
# Testar endpoints específicos (ajuste conforme sua API)
curl -X GET https://seu-dominio.com/api/v1/usuario/
curl -X POST https://seu-dominio.com/api/v1/conta/login
curl -X GET https://seu-dominio.com/api/v1/web_link/
```

## 📊 Monitoramento Contínuo

### Comandos Úteis

```bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f

# Logs de serviço específico
docker-compose logs -f app
docker-compose logs -f worker

# Uso de recursos
docker stats

# Verificar espaço em disco
docker system df

# Limpar recursos não utilizados
docker system prune
```

### Logs Importantes

```bash
# Verificar logs de inicialização
docker-compose logs app | grep -E "(ready|started|error|exception)"

# Verificar logs do worker
docker-compose logs worker | grep -E "(ready|started|error|exception)"

# Verificar logs de banco
docker-compose logs postgres | grep -E "(ready|started|error|exception)"
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Serviço não responde**
   ```bash
   # Verificar se está rodando
   docker-compose ps
   
   # Verificar logs
   docker-compose logs servico
   
   # Reiniciar serviço
   docker-compose restart servico
   ```

2. **Erro de conexão com banco**
   ```bash
   # Verificar se PostgreSQL está rodando
   docker-compose exec postgres pg_isready
   
   # Verificar variáveis de ambiente
   docker-compose exec app env | grep DATABASE
   ```

3. **Worker não processa tasks**
   ```bash
   # Verificar se worker está conectado
   docker-compose exec worker celery -A api.utils.celery_app inspect active
   
   # Verificar Redis
   docker-compose exec redis redis-cli ping
   ```

4. **API retorna erro 500**
   ```bash
   # Verificar logs da aplicação
   docker-compose logs app
   
   # Verificar se migrations foram executadas
   docker-compose exec app alembic current
   ```

### Debug Avançado

```bash
# Entrar no container da aplicação
docker-compose exec app bash

# Entrar no container do worker
docker-compose exec worker bash

# Verificar processos dentro do container
docker-compose exec app ps aux

# Verificar uso de memória
docker-compose exec app free -h

# Verificar espaço em disco
docker-compose exec app df -h
```

## 📈 Métricas de Performance

### Teste de Carga Simples

```bash
# Teste com múltiplas requisições
for i in {1..10}; do
  curl -s https://seu-dominio.com/health &
done
wait

# Medir tempo de resposta
time curl https://seu-dominio.com/health
```

### Monitoramento de Recursos

```bash
# Verificar uso de CPU e memória
docker stats --no-stream

# Verificar logs de performance
docker-compose logs app | grep -E "(slow|timeout|performance)"
```

## ✅ Checklist de Deploy

Antes de considerar o deploy como bem-sucedido:

- [ ] Health check retorna 200
- [ ] Swagger UI carrega corretamente
- [ ] Banco de dados conecta
- [ ] Redis responde
- [ ] Celery worker está ativo
- [ ] Migrations executadas
- [ ] Logs sem erros críticos
- [ ] Endpoints principais funcionando
- [ ] Performance aceitável (< 2s resposta)
- [ ] Headers de segurança presentes

## 🎯 Próximos Passos

Após confirmar que tudo está funcionando:

1. **Configurar monitoramento** (opcional)
2. **Configurar backup** do banco de dados
3. **Configurar SSL/HTTPS** no Coolify
4. **Configurar domínio personalizado**
5. **Configurar CI/CD** para deploys automáticos
6. **Documentar** endpoints para frontend
