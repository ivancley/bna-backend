#!/usr/bin/env python3
"""
Script para testar o scraping com diferentes URLs, incluindo sites problemáticos.

Uso:
    python scripts/test_scraping.py

Este script testa o scraping com diferentes URLs para verificar se as melhorias
resolveram os problemas de timeout.
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.v1.web_link.scraping.scraping import url_to_json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URLs de teste
TEST_URLS = [
    "https://example.com",  # Site simples
    "https://httpbin.org/html",  # Site de teste
    "https://180graus.com/",  # Site problemático
    "https://www.uol.com.br/",  # Site brasileiro grande
    "https://g1.globo.com/",  # Site brasileiro grande
]

def test_scraping():
    """Testa o scraping com diferentes URLs."""
    print("=" * 80)
    print("🧪 TESTE DE SCRAPING COM MELHORIAS")
    print("=" * 80)
    
    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n{'='*60}")
        print(f"📝 TESTE {i}: {url}")
        print(f"{'='*60}")
        
        try:
            print(f"🔄 Iniciando scraping...")
            result = url_to_json(url, timeout=90.0, max_retries=3)
            
            print(f"✅ Sucesso!")
            print(f"   - Título: {result.title[:100] if result.title else 'N/A'}...")
            print(f"   - Descrição: {result.description[:100] if result.description else 'N/A'}...")
            print(f"   - Tamanho do texto: {len(result.text_full) if result.text_full else 0} caracteres")
            print(f"   - H1 encontrados: {len(result.headings.h1) if result.headings else 0}")
            print(f"   - H2 encontrados: {len(result.headings.h2) if result.headings else 0}")
            print(f"   - H3 encontrados: {len(result.headings.h3) if result.headings else 0}")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            print(f"   Tipo do erro: {type(e).__name__}")
    
    print(f"\n{'='*80}")
    print("✅ TESTES CONCLUÍDOS!")
    print(f"{'='*80}")

def test_specific_url():
    """Testa uma URL específica."""
    print("\n" + "="*80)
    print("🎯 TESTE COM URL ESPECÍFICA")
    print("="*80)
    
    # Modifique esta URL para testar
    url = "https://180graus.com/"
    
    print(f"URL: {url}")
    print("Iniciando teste...")
    
    try:
        result = url_to_json(url, timeout=90.0, max_retries=3)
        
        print(f"\n✅ SUCESSO!")
        print(f"Título: {result.title}")
        print(f"Descrição: {result.description}")
        print(f"Tamanho do texto: {len(result.text_full) if result.text_full else 0} caracteres")
        
        if result.headings:
            print(f"\n📋 HEADINGS:")
            print(f"H1: {result.headings.h1}")
            print(f"H2: {result.headings.h2}")
            print(f"H3: {result.headings.h3}")
        
        if result.text_full:
            print(f"\n📄 PRIMEIROS 500 CARACTERES DO TEXTO:")
            print("-" * 50)
            print(result.text_full[:500])
            print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando testes de scraping...")
    
    # Executar testes gerais
    test_scraping()
    
    # Executar teste específico
    test_specific_url()
    
    print("\n🎉 Testes finalizados!")
