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
    Cria e configura uma instância do Chrome WebDriver com opções anti-detecção.
    
    Returns:
        webdriver.Chrome: Instância configurada do Chrome WebDriver
    """
    chrome_options = Options()
    
    # Modo headless (sem interface gráfica)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Configurações de window para parecer mais natural
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    # User Agent aleatório
    chrome_options.add_argument(f"user-agent={_get_random_user_agent()}")
    
    # Configurações anti-detecção
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Configurações de performance
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    
    # Preferências adicionais
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Cria o driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Script para mascarar detecção de Selenium
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
        """
    })
    
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


def url_to_json(url: str, timeout: float = 30.0, max_retries: int = 2) -> PageContent:
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
            driver.set_page_load_timeout(timeout)
            
            # Acessa a URL
            driver.get(url)
            
            # Delay aleatório para simular comportamento humano
            time.sleep(random.uniform(1, 3))
            
            # Aguarda até que o body esteja presente (indica que a página carregou)
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Aguarda um pouco mais para JavaScript dinâmico carregar
            time.sleep(random.uniform(1, 2))
            
            # Scroll suave para simular comportamento humano e carregar lazy load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 0);")
            
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