from __future__ import annotations
import os
import re
import sys
from typing import Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

from api.v1._shared.custom_schemas import HeadingsData, OpenGraphData, PageContent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ContentFetcher/1.0; +https://example.com/bot)"
}


def _clean_text(text: str) -> str:
    # Normaliza espaços
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
    try:
        return urlparse(url).netloc
    except Exception:
        return ""

def url_to_json(url: str, timeout: float = 15.0) -> PageContent:
    """
    Faz o download de uma URL e retorna um objeto PageContent com o conteúdo extraído.
    
    Args:
        url: URL da página a ser extraída
        timeout: Tempo máximo de espera em segundos
        
    Returns:
        PageContent: Objeto com título, descrição, conteúdo e metadados da página
        
    Raises:
        requests.RequestException: Se houver erro na requisição HTTP
        ValueError: Se o conteúdo não for HTML válido
    """
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
    content_type = resp.headers.get("Content-Type", "").lower()
    
    # Verifica se é HTML
    if not ("text/html" in content_type or "<html" in resp.text.lower()):
        raise ValueError(f"Conteúdo não é HTML válido. Content-Type: {content_type}")
    
    # Extrai dados da página HTML
    soup = BeautifulSoup(resp.text, "lxml")
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