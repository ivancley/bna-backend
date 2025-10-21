# Scripts de Manutenção

Scripts utilitários para manutenção do sistema RAG.

## 🔧 Scripts Disponíveis

### 1. `check_celery_tasks.py`
Verifica quais tasks estão registradas no Celery e suas configurações de roteamento.

**Uso:**
```bash
python scripts/check_celery_tasks.py
```

**Mostra:**
- ✅ Lista de todas as tasks registradas
- 🗺️ Configuração de rotas (task → fila)
- 📊 Separação por tipo (email, scraping, etc)

---

### 2. `test_task_import.py`
Testa se a task de scraping pode ser importada e registrada corretamente.

**Uso:**
```bash
python scripts/test_task_import.py
```

**Verifica:**
- Importação do celery_app
- Importação da task scrape_url_task
- Se a task está registrada
- Se pode criar signatures

---

### 3. `clear_conhecimentos.py`
Limpa todos os conhecimentos (embeddings) do banco de dados.

**Uso:**
```bash
python scripts/clear_conhecimentos.py
```

**Quando usar:**
- Após correções no formato de embeddings
- Para resetar completamente o índice vetorial
- Antes de re-ingerir todos os WebLinks

---

### 4. `reingest_weblinks.py`
Re-ingere todos os WebLinks existentes, disparando tasks Celery para scraping e embedding.

**Uso:**
```bash
python scripts/reingest_weblinks.py
```

**Requisitos:**
- Celery worker deve estar rodando
- Redis deve estar ativo
- OpenAI API key configurada

**Quando usar:**
- Após limpar os conhecimentos
- Após mudanças na lógica de chunking/embedding
- Para reprocessar WebLinks com novos parâmetros

---

## 📋 Fluxo Recomendado

### Diagnóstico de problemas com Celery:

```bash
# 1. Verifica se tasks estão registradas
python scripts/check_celery_tasks.py

# 2. Testa importação da task
python scripts/test_task_import.py
```

### Re-ingestão de WebLinks após correções:

```bash
# 1. Limpa conhecimentos antigos
python scripts/clear_conhecimentos.py

# 2. Re-ingere todos os WebLinks
python scripts/reingest_weblinks.py

# 3. Aguarda processamento
# Monitore os logs do Celery worker
```

---

## ⚠️ Avisos

- **SEMPRE** faça backup antes de executar scripts de limpeza
- Confirme que o Celery worker está rodando antes de re-ingerir
- A re-ingestão pode demorar dependendo do número de WebLinks
- Custos de API da OpenAI serão aplicados novamente

