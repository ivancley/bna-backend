# Web Scraping com Selenium

Este módulo implementa web scraping usando **Selenium WebDriver** com Chrome headless, incluindo estratégias anti-detecção para contornar bloqueios de sites.

## 🚀 Funcionalidades

- **Selenium WebDriver**: Renderiza JavaScript e conteúdo dinâmico
- **Chrome Headless**: Execução sem interface gráfica
- **Anti-detecção**: 
  - User-Agent aleatório
  - Delays aleatórios entre ações
  - Mascaramento de propriedades do Selenium
  - Scroll suave para simular comportamento humano
- **Espera inteligente**: Aguarda elementos da página carregarem
- **Retry automático**: Até 3 tentativas em caso de falha
- **Extração robusta**: BeautifulSoup para parsing do HTML renderizado

## 📦 Dependências

As seguintes dependências foram adicionadas ao `requirements.txt`:

```
selenium==4.27.1
webdriver-manager==4.0.2
```

## 🐳 Docker

O `Dockerfile.worker` foi atualizado para incluir:

- Google Chrome Stable
- ChromeDriver (gerenciado automaticamente via webdriver-manager)
- Dependências do sistema necessárias

## 🔧 Uso

```python
from api.v1.web_link.scraping.scraping import url_to_json

# Faz scraping de uma URL
page_content = url_to_json(
    url="https://example.com",
    timeout=30.0,  # Timeout em segundos (padrão: 30s)
    max_retries=2  # Número de tentativas (padrão: 2)
)

# Acessa os dados extraídos
print(page_content.title)
print(page_content.description)
print(page_content.text_full)
```

## 🛠️ Instalação Local (Desenvolvimento)

Para testar localmente, você precisa instalar o Chrome/Chromium:

### Ubuntu/Debian:
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```

### macOS:
```bash
brew install --cask google-chrome
```

### Instalar dependências Python:
```bash
pip install -r requirements.txt
```

## 🚦 Deploy

No deploy com Docker, o Chrome já estará instalado automaticamente via `Dockerfile.worker`.

Para rebuild do container worker:

```bash
docker-compose build worker
docker-compose up -d worker
```

## ⚙️ Configurações Anti-Detecção

O scraper implementa várias técnicas para evitar detecção:

1. **User-Agent Rotation**: 6 diferentes user-agents são alternados aleatoriamente
2. **Mascaramento de WebDriver**: Remove propriedades que identificam Selenium
3. **Delays Aleatórios**: Entre 1-3s para simular leitura humana
4. **Scroll Behavior**: Simula scroll natural da página
5. **Window Size**: Define tamanho de janela realista (1920x1080)

## 📝 Logs

O módulo gera logs detalhados para debug:

```
[SELENIUM] Tentativa 1/3 - Acessando: https://example.com
[SELENIUM] Página carregada com sucesso: https://example.com
```

## ⚠️ Limitações

- **CAPTCHA**: Não há suporte para resolução automática de CAPTCHA
- **Recursos**: Consome mais memória e CPU que scraping via `requests`
- **Velocidade**: Mais lento que scraping tradicional (necessário para bypass de proteções)

## 🔍 Troubleshooting

### Chrome não encontrado no container:
```bash
# Verificar instalação
docker-compose exec worker google-chrome --version

# Rebuild do container
docker-compose build --no-cache worker
```

### Timeout frequente:
```python
# Aumente o timeout
page_content = url_to_json(url, timeout=60.0, max_retries=3)
```

### Erro de WebDriver:
O `webdriver-manager` baixa automaticamente o ChromeDriver compatível. Se houver erro, pode ser problema de rede ou permissões.

## 📄 Estrutura de Retorno

```python
PageContent(
    title: str | None,
    description: str | None,
    keywords: str | None,
    canonical: str | None,
    headings: HeadingsData(h1=[], h2=[], h3=[]),
    text_full: str,  # Até 20KB de texto
    og: OpenGraphData(type=None, url=None, image=None)
)
```

