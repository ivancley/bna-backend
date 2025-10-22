from __future__ import annotations
import os
import random
import re
import sys
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

from api.v1._shared.custom_schemas import HeadingsData, OpenGraphData, PageContent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# User Agents variados para anti-detecção
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]


def _get_random_user_agent() -> str:
    """Retorna um User-Agent aleatório para evitar detecção."""
    return random.choice(USER_AGENTS)


def _create_chrome_driver() -> webdriver.Chrome:
    """
    Cria e configura uma instância do Chrome WebDriver com opções otimizadas.
    Tenta primeiro com headless, se falhar, usa modo normal.
    
    Returns:
        webdriver.Chrome: Instância configurada do Chrome WebDriver
    """
    
    # Tentar primeiro com headless
    try:
        return _create_chrome_driver_headless()
    except Exception as e:
        print(f"[SELENIUM] Headless falhou ({e}), tentando modo normal...")
        return _create_chrome_driver_normal()


def _create_chrome_driver_headless() -> webdriver.Chrome:
    """Cria driver em modo headless."""
    chrome_options = Options()
    
    # MODO HEADLESS - Não abre navegador na tela
    chrome_options.add_argument("--headless")
    
    # User-Agent realista e aleatório
    user_agent = _get_random_user_agent()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    
    # Anti-detecção básica
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # DESABILITAR RECURSOS DESNECESSÁRIOS - Foco apenas em texto/HTML
    chrome_options.add_argument("--disable-images")           # Sem imagens
    chrome_options.add_argument("--disable-javascript")        # Sem JavaScript
    chrome_options.add_argument("--disable-css")              # Sem CSS
    chrome_options.add_argument("--disable-plugins")           # Sem plugins
    chrome_options.add_argument("--disable-extensions")       # Sem extensões
    chrome_options.add_argument("--disable-web-security")      # Sem verificações de segurança
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Performance e recursos
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Timeout e carregamento otimizado
    chrome_options.add_argument("--timeout=120")               # 2 minutos
    chrome_options.add_argument("--page-load-strategy=normal")
    chrome_options.add_argument("--dns-prefetch-disable")
    
    # Janela e display (headless)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    # Configurações básicas para headless
    
    # Headers mínimos - apenas HTML
    chrome_options.add_argument("--accept-language=pt-BR,pt;q=0.9,en;q=0.8")
    chrome_options.add_argument("--accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    
    # Configurações específicas para sites brasileiros
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")
    
    # Logs silenciosos
    chrome_options.add_argument("--log-level=3")              # Apenas erros fatais
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Configurações adicionais do driver - Timeout maior para sites lentos
    driver.set_page_load_timeout(120)  # 2 minutos
    driver.implicitly_wait(5)          # 5 segundos
    
    # Executar scripts para remover propriedades de automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
    
    return driver


def _create_chrome_driver_normal() -> webdriver.Chrome:
    """Cria driver em modo normal (navegador visível)."""
    chrome_options = Options()
    
    # MODO NORMAL - Navegador aparecerá na tela
    # chrome_options.add_argument("--headless")  # COMENTADO
    
    # User-Agent realista e aleatório
    user_agent = _get_random_user_agent()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    
    # Anti-detecção básica
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # DESABILITAR RECURSOS DESNECESSÁRIOS - Foco apenas em texto/HTML
    chrome_options.add_argument("--disable-images")           # Sem imagens
    chrome_options.add_argument("--disable-javascript")        # Sem JavaScript
    chrome_options.add_argument("--disable-css")              # Sem CSS
    chrome_options.add_argument("--disable-plugins")           # Sem plugins
    chrome_options.add_argument("--disable-extensions")       # Sem extensões
    chrome_options.add_argument("--disable-web-security")      # Sem verificações de segurança
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Performance e recursos
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Timeout e carregamento otimizado
    chrome_options.add_argument("--timeout=120")               # 2 minutos
    chrome_options.add_argument("--page-load-strategy=normal")
    chrome_options.add_argument("--dns-prefetch-disable")
    
    # Janela e display
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Headers mínimos - apenas HTML
    chrome_options.add_argument("--accept-language=pt-BR,pt;q=0.9,en;q=0.8")
    chrome_options.add_argument("--accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    
    # Configurações específicas para sites brasileiros
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")
    
    # Logs silenciosos
    chrome_options.add_argument("--log-level=3")              # Apenas erros fatais
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Configurações adicionais do driver - Timeout maior para sites lentos
    driver.set_page_load_timeout(120)  # 2 minutos
    driver.implicitly_wait(5)          # 5 segundos
    
    # Executar scripts para remover propriedades de automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
    
    return driver


def _clean_text(text: str) -> str:
    """Normaliza espaços em branco."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_meta(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    def meta(name: str) -> Optional[str]:
        tag = soup.find("meta", attrs={"name": name})
        return tag.get("content") if tag and tag.has_attr("content") else None

    def prop(property_name: str) -> Optional[str]:
        tag = soup.find("meta", attrs={"property": property_name})
        return tag.get("content") if tag and tag.has_attr("content") else None

    metas = {
        "title": (soup.title.string if soup.title else None) or prop("og:title"),
        "description": meta("description") or prop("og:description"),
        "keywords": meta("keywords"),
        "og:type": prop("og:type"),
        "og:image": prop("og:image"),
        "og:url": prop("og:url"),
        "canonical": None,
    }

    link_canonical = soup.find("link", rel=lambda v: v and "canonical" in [x.lower() for x in (v if isinstance(v, list) else [v])])
    if link_canonical and link_canonical.has_attr("href"):
        metas["canonical"] = link_canonical["href"]

    return metas

def _extract_headings(soup: BeautifulSoup) -> Dict[str, List[str]]:
    data: Dict[str, List[str]] = {"h1": [], "h2": [], "h3": []}
    for level in ("h1", "h2", "h3"):
        for tag in soup.find_all(level):
            txt = _clean_text(tag.get_text(" "))
            if txt:
                data[level].append(txt)
    return data

def _extract_main_text(soup: BeautifulSoup, min_len: int = 40) -> str:
    """
    Extrai um 'texto principal' simples juntando parágrafos relevantes.
    """
    # Remove elementos que raramente contribuem para o conteúdo
    for bad in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "aside"]):
        bad.decompose()

    paragraphs = []
    for p in soup.find_all("p"):
        txt = _clean_text(p.get_text(" "))
        if len(txt) >= min_len:
            paragraphs.append(txt)

    # Limita tamanho para evitar JSON enorme
    joined = "\n\n".join(paragraphs)
    return joined[:20000]  # ~20KB de texto

def _domain(url: str) -> str:
    """Extrai o domínio de uma URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def url_to_json(url: str, timeout: float = 90.0, max_retries: int = 3) -> PageContent:
    """
    Faz o scraping de uma URL usando Selenium e retorna um objeto PageContent com o conteúdo extraído.
    
    Estratégias anti-detecção implementadas:
    - User-Agent aleatório
    - Delays aleatórios entre ações
    - Mascaramento de propriedades do Selenium
    - Espera inteligente por elementos da página
    
    Args:
        url: URL da página a ser extraída
        timeout: Tempo máximo de espera em segundos (padrão: 30s)
        max_retries: Número máximo de tentativas em caso de falha (padrão: 2)
        
    Returns:
        PageContent: Objeto com título, descrição, conteúdo e metadados da página
        
    Raises:
        TimeoutException: Se a página não carregar dentro do timeout
        WebDriverException: Se houver erro no WebDriver
        ValueError: Se o conteúdo não for HTML válido
    """
    driver = None
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            print(f"[SELENIUM] Tentativa {attempt + 1}/{max_retries + 1} - Acessando: {url}")
            
            # Delay aleatório entre tentativas (anti-detecção)
            if attempt > 0:
                delay = random.uniform(2, 5)
                print(f"[SELENIUM] Aguardando {delay:.2f}s antes de tentar novamente...")
                time.sleep(delay)
            
            # Cria o driver Chrome
            driver = _create_chrome_driver()
            
            # Acessa a URL
            print(f"[SELENIUM] Carregando página: {url}")
            driver.get(url)
            
            # Aguarda até que o body esteja presente (indica que a página carregou)
            wait = WebDriverWait(driver, timeout)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                print(f"[SELENIUM] Body carregado - aguardando 30s para conteúdo completo...")
            except TimeoutException:
                print(f"[SELENIUM] Timeout aguardando body, tentando continuar...")
            
            # AGUARDA 30 SEGUNDOS para o conteúdo carregar completamente
            # Mesmo que o loading continue girando, o conteúdo HTML já está disponível
            print(f"[SELENIUM] Aguardando 30 segundos para conteúdo completo...")
            time.sleep(30)
            
            # Verifica se a página carregou verificando o título
            try:
                page_title = driver.title
                if not page_title or page_title.strip() == "":
                    print(f"[SELENIUM] Página sem título")
                else:
                    print(f"[SELENIUM] Título da página: {page_title[:50]}...")
            except Exception as e:
                print(f"[SELENIUM] Erro ao obter título: {e}")
            
            print(f"[SELENIUM] Extraindo conteúdo HTML...")
            
            # Obtém o HTML renderizado
            page_source = driver.page_source
            
            # Verifica se é HTML
            if not ("<html" in page_source.lower() or "<body" in page_source.lower()):
                raise ValueError(f"Conteúdo não é HTML válido")
            
            print(f"[SELENIUM] Página carregada com sucesso: {url}")
            
            # Extrai dados da página HTML com BeautifulSoup
            soup = BeautifulSoup(page_source, "lxml")
            meta = _extract_meta(soup)
            headings_dict = _extract_headings(soup)
            main_text = _extract_main_text(soup)
            
            # Cria objetos dos schemas
            headings_data = HeadingsData(
                h1=headings_dict.get("h1", []),
                h2=headings_dict.get("h2", []),
                h3=headings_dict.get("h3", [])
            )
            
            og_data = OpenGraphData(
                type=meta.get("og:type"),
                url=meta.get("og:url"),
                image=meta.get("og:image")
            )
            
            # Retorna objeto PageContent
            return PageContent(
                title=meta.get("title"),
                description=meta.get("description"),
                keywords=meta.get("keywords"),
                canonical=meta.get("canonical"),
                headings=headings_data,
                text_full=main_text,
                og=og_data
            )
            
        except TimeoutException as e:
            last_exception = e
            print(f"[SELENIUM] Timeout na tentativa {attempt + 1}: {str(e)}")
            if attempt >= max_retries:
                raise TimeoutException(
                    f"Timeout após {max_retries + 1} tentativas ao acessar {url}. "
                    f"A página não carregou dentro do tempo limite de {timeout}s."
                )
                
        except WebDriverException as e:
            last_exception = e
            print(f"[SELENIUM] Erro no WebDriver na tentativa {attempt + 1}: {str(e)}")
            if attempt >= max_retries:
                raise WebDriverException(
                    f"Erro no WebDriver após {max_retries + 1} tentativas: {str(e)}"
                )
                
        except Exception as e:
            last_exception = e
            print(f"[SELENIUM] Erro inesperado na tentativa {attempt + 1}: {str(e)}")
            if attempt >= max_retries:
                raise
                
        finally:
            # Sempre fecha o driver para liberar recursos
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"[SELENIUM] Erro ao fechar driver: {str(e)}")
                driver = None
    
    # Se chegou aqui, todas as tentativas falharam
    if last_exception:
        raise last_exception
    raise Exception(f"Falha ao acessar {url} após {max_retries + 1} tentativas")