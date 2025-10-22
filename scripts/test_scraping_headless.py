#!/usr/bin/env python3
"""
Script para testar o scraping otimizado com modo headless e foco em texto.

Uso:
    python scripts/test_scraping_headless.py

Este script testa o scraping com as novas configurações:
- Modo headless (sem abrir navegador)
- Desabilita recursos desnecessários (imagens, CSS, JS)
- Aguarda 30 segundos após body carregar
- Foca apenas em texto e estrutura HTML
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.v1.web_link.scraping.scraping import url_to_json
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URLs de teste
TEST_URLS = [
    "https://180graus.com/",  # Site problemático
    "https://www.uol.com.br/",  # Site brasileiro grande
]

def test_headless_scraping():
    """Testa o scraping em modo headless."""
    print("=" * 80)
    print("🧪 TESTE DE SCRAPING HEADLESS OTIMIZADO")
    print("=" * 80)
    print("✅ Modo headless ativado (navegador não aparecerá na tela)")
    print("✅ Recursos desnecessários desabilitados (imagens, CSS, JS)")
    print("✅ Aguardando 30s após body carregar")
    print("✅ Foco apenas em texto e estrutura HTML")
    print("=" * 80)
    
    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n{'='*60}")
        print(f"📝 TESTE {i}: {url}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            print(f"🔄 Iniciando scraping (modo headless)...")
            result = url_to_json(url, timeout=30.0, max_retries=2)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Sucesso! Tempo total: {duration:.1f}s")
            print(f"   - Título: {result.title[:100] if result.title else 'N/A'}...")
            print(f"   - Descrição: {result.description[:100] if result.description else 'N/A'}...")
            print(f"   - Tamanho do texto: {len(result.text_full) if result.text_full else 0} caracteres")
            print(f"Texto completo: {result.text_full}")
            
            if result.headings:
                print(f"   - H1 encontrados: {len(result.headings.h1)}")
                print(f"   - H2 encontrados: {len(result.headings.h2)}")
                print(f"   - H3 encontrados: {len(result.headings.h3)}")
                
                if result.headings.h1:
                    print(f"   - Primeiro H1: {result.headings.h1[0][:50]}...")
            
            if result.text_full:
                print(f"\n📄 PRIMEIROS 200 CARACTERES DO TEXTO:")
                print("-" * 50)
                print(result.text_full[:200])
                print("-" * 50)
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Erro após {duration:.1f}s: {str(e)}")
            print(f"   Tipo do erro: {type(e).__name__}")
    
    print(f"\n{'='*80}")
    print("✅ TESTES CONCLUÍDOS!")
    print(f"{'='*80}")

def test_180graus_specific():
    """Teste específico para 180graus.com."""
    print("\n" + "="*80)
    print("🎯 TESTE ESPECÍFICO: 180graus.com")
    print("="*80)
    
    url = "https://180graus.com/"
    print(f"URL: {url}")
    print("Iniciando teste específico...")
    
    start_time = time.time()
    
    try:
        result = url_to_json(url, timeout=120.0, max_retries=2)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ SUCESSO! Tempo total: {duration:.1f}s")
        print(f"Título: {result.title}")
        print(f"Descrição: {result.description}")
        print(f"Tamanho do texto: {len(result.text_full) if result.text_full else 0} caracteres")
        print(f"Texto completo: {result.text_full}")
        
        if result.headings:
            print(f"\n📋 HEADINGS ENCONTRADOS:")
            print(f"H1 ({len(result.headings.h1)}): {result.headings.h1}")
            print(f"H2 ({len(result.headings.h2)}): {result.headings.h2}")
            print(f"H3 ({len(result.headings.h3)}): {result.headings.h3}")
        
        if result.text_full:
            print(f"\n📄 PRIMEIROS 500 CARACTERES DO TEXTO:")
            print("-" * 60)
            print(result.text_full[:500])
            print("-" * 60)
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n❌ ERRO após {duration:.1f}s: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando testes de scraping headless otimizado...")
    
    # Executar testes gerais
    test_headless_scraping()
    
    # Executar teste específico
    #test_180graus_specific()
    
    print("\n🎉 Testes finalizados!")
