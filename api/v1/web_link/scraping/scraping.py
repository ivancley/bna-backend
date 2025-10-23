from __future__ import annotations
import os
import random
import re
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    return random.choice(USER_AGENTS)

def _create_chrome_driver_headless() -> tuple[webdriver.Chrome, str]:
    """Cria driver em modo headless invisível, com JS habilitado e imagens desabilitadas via prefs."""
    import tempfile
    import os
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # headless invisível moderno
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # CORREÇÃO: Criar diretório temporário único para cada instância
    temp_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    # CORREÇÃO: Configurar cache do Selenium em diretório com permissão
    cache_dir = "/tmp/selenium_cache"
    os.makedirs(cache_dir, exist_ok=True)
    chrome_options.add_argument(f"--disk-cache-dir={cache_dir}")
    
    # CORREÇÃO ADICIONAL: Configurar variáveis de ambiente para Selenium
    os.environ['SELENIUM_CACHE_DIR'] = cache_dir
    os.environ['SELENIUM_USER_DATA_DIR'] = temp_dir
    
    # CORREÇÃO: Configurações adicionais para containers
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    #chrome_options.add_argument("--disable-javascript")  # Desabilitar JS para melhor performance
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--remote-debugging-port=0")  # Porta aleatória para evitar conflitos
    
    # CORREÇÃO CRÍTICA: Desabilitar completamente o cache padrão do Selenium
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")

    # User-Agent realista e aleatório
    user_agent = _get_random_user_agent()
    chrome_options.add_argument(f"--user-agent={user_agent}")

    # Anti-detecção básica
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Preferências para acelerar: desabilitar imagens (JS permanece ATIVADO)
    chrome_prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.images": 2,
        "profile.managed_default_content_settings.stylesheets": 1,  # CSS habilitado
        "profile.managed_default_content_settings.javascript": 1,   # JS habilitado
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    # Aceite de idioma e formato
    chrome_options.add_argument("--accept-language=pt-BR,pt;q=0.9,en;q=0.8")

    # Não aguarda carregamento total da página (controle manual via polling)
    chrome_options.page_load_strategy = "none"

    # Logs silenciosos
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)

    # Tempo de carregamento por navegação (defensivo — usamos polling mesmo com page_load_strategy='none')
    driver.set_page_load_timeout(30)

    # Mascaramento adicional
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
    except Exception:
        pass

    return driver, temp_dir

def _cleanup_temp_dirs(temp_dir: str):
    """Limpa diretórios temporários criados pelo Chrome."""
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

def _clean_text(text: str) -> str:
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
    if soup.body:
        text = soup.body.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)
    return text[:20000]

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""

def _poll_until_ready_or_timeout(
    driver: webdriver.Chrome,
    url: str,
    max_seconds: float = 30.0,
    poll_interval: float = 0.25
) -> Tuple[str, bool]:
    """
    Navega e faz polling até existir <body> OU estourar o tempo.
    Retorna (page_source, timed_out).
    """
    start = time.monotonic()
    timed_out = False

    # Tenta navegar (não bloqueante por 'none', mas ainda pode esperar um pouco).
    try:
        driver.get(url)
    except TimeoutException:
        # Se houve timeout do próprio get, seguimos para capturar o que tiver.
        pass
    except WebDriverException:
        # Repassar para o chamador tratar retry
        raise

    # Aguarda presença de <body> ou até estourar o tempo
    body_found = False
    while True:
        elapsed = time.monotonic() - start
        if elapsed >= max_seconds:
            timed_out = True
            break
        try:
            # Aguarda rapidamente pela presença do body (não bloqueante por muito tempo)
            WebDriverWait(driver, poll_interval).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            body_found = True
            break
        except TimeoutException:
            # segue o loop até estourar o tempo
            continue

    # Coleta o que tiver
    try:
        page_source = driver.page_source or ""
    except Exception:
        page_source = ""

    # Se o body apareceu muito cedo, dá um micro-respiro para render dinâmico (sem estourar 30s)
    if body_found and not timed_out:
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= max_seconds:
                timed_out = True
                break
            # Pequeno polling para permitir carregamento incremental
            time.sleep(poll_interval)
            # Heurística simples: se DOM cresce, continua mais um ciclo; senão, para
            try:
                current_len = len(driver.page_source or "")
            except Exception:
                current_len = len(page_source)
            if current_len <= len(page_source):
                break
            page_source = driver.page_source or ""

    return page_source, timed_out

def url_to_json(url: str, timeout: float = 30.0, max_retries: int = 1) -> PageContent:
    """
    Faz o scraping de uma URL usando Selenium headless e retorna um PageContent.
    - Navegação+render por tentativa: máx. 30s (default).
    - Até 2 tentativas (max_retries=1 => 2 tentativas).
    - Se estourar o tempo, retorna conteúdo parcial com timed_out=True.
    - Extração (BeautifulSoup) ocorre fora do limite de 30s.

    Raises:
        WebDriverException em falhas críticas do WebDriver após as tentativas.
        ValueError se nenhum HTML válido for obtido.
    """
    # Garanta no máx. 2 tentativas
    max_retries = min(max_retries, 1)

    best_html = ""
    best_timed_out = False
    last_exception = None

    for attempt in range(max_retries + 1):
        driver = None
        temp_dir = None
        try:
            driver, temp_dir = _create_chrome_driver_headless()
            html, timed_out = _poll_until_ready_or_timeout(driver, url, max_seconds=timeout, poll_interval=0.25)

            # Guarda o "melhor" HTML (por tamanho) entre tentativas
            if len(html) > len(best_html):
                best_html = html
                best_timed_out = timed_out

            # Se já temos algo razoável, podemos encerrar cedo (por ex., body presente)
            if html and ("<html" in html.lower() or "<body" in html.lower()):
                # se não estourou, ótimo — se estourou, mesmo assim retornaremos parcial
                break

        except WebDriverException as e:
            last_exception = e
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            # CORREÇÃO: Limpa diretórios temporários
            if temp_dir:
                _cleanup_temp_dirs(temp_dir)

    if not best_html:
        # Se nada foi obtido, propaga última exceção ou gera erro claro
        if last_exception:
            raise WebDriverException(f"Falha ao carregar {url}: {last_exception}")
        raise ValueError(f"Nenhum HTML válido obtido em {url}")

    # ===== Extração (fora do limite de 30s) =====
    soup = BeautifulSoup(best_html, "lxml")
    meta = _extract_meta(soup)
    headings_dict = _extract_headings(soup)
    main_text = _extract_main_text(soup)
    
    #print(soup.body.prettify())
    #print(soup.body.get_text(" ", strip=True))

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

    # Retorna objeto PageContent — inclui timed_out=True/False conforme solicitado
    return PageContent(
        title=meta.get("title"),
        description=meta.get("description"),
        keywords=meta.get("keywords"),
        canonical=meta.get("canonical"),
        headings=headings_data,
        text_full=main_text,
        og=og_data,
        timed_out=best_timed_out  # <- NOVO CAMPO
    )
