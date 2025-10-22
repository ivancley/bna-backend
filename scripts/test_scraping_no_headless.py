#!/usr/bin/env python3
"""
Script para testar o scraping SEM headless primeiro, para verificar se funciona.

Uso:
    python scripts/test_scraping_no_headless.py

Este script testa o scraping sem headless para verificar se o problema
é específico do modo headless ou do scraping em geral.
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

def test_without_headless():
    """Testa o scraping sem headless."""
    print("=" * 80)
    print("🧪 TESTE DE SCRAPING SEM HEADLESS")
    print("=" * 80)
    print("⚠️  O navegador VAI aparecer na tela (modo normal)")
    print("✅ Recursos desnecessários desabilitados (imagens, CSS, JS)")
    print("✅ Aguardando 30s após body carregar")
    print("✅ Foco apenas em texto e estrutura HTML")
    print("=" * 80)
    
    # Modificar temporariamente o código para não usar headless
    import api.v1.web_link.scraping.scraping as scraping_module
    
    # Salvar a função original
    original_create_driver = scraping_module._create_chrome_driver
    
    def create_driver_without_headless():
        """Versão sem headless para teste."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        
        # NÃO usar headless - navegador aparecerá na tela
        # chrome_options.add_argument("--headless")  # COMENTADO
        
        # User-Agent realista
        user_agent = scraping_module._get_random_user_agent()
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Anti-detecção básica
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # DESABILITAR RECURSOS DESNECESSÁRIOS
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-css")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        
        # Performance
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        
        # Timeout
        chrome_options.add_argument("--timeout=120")
        chrome_options.add_argument("--page-load-strategy=normal")
        chrome_options.add_argument("--dns-prefetch-disable")
        
        # Janela
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        # Headers
        chrome_options.add_argument("--accept-language=pt-BR,pt;q=0.9,en;q=0.8")
        chrome_options.add_argument("--accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        
        # Configurações específicas
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-domain-reliability")
        
        # Logs
        chrome_options.add_argument("--log-level=3")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Configurações do driver
        driver.set_page_load_timeout(120)
        driver.implicitly_wait(5)
        
        # Scripts anti-detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
        
        return driver
    
    # Substituir temporariamente a função
    scraping_module._create_chrome_driver = create_driver_without_headless
    
    try:
        # Testar com uma URL simples
        url = "https://example.com"
        print(f"\n🔄 Testando: {url}")
        print("⚠️  O navegador Chrome vai abrir na sua tela!")
        
        start_time = time.time()
        result = url_to_json(url, timeout=120.0, max_retries=2)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ SUCESSO! Tempo total: {duration:.1f}s")
        print(f"Título: {result.title}")
        print(f"Descrição: {result.description}")
        print(f"Tamanho do texto: {len(result.text_full) if result.text_full else 0} caracteres")
        
        if result.text_full:
            print(f"\n📄 PRIMEIROS 200 CARACTERES:")
            print("-" * 50)
            print(result.text_full[:200])
            print("-" * 50)
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n❌ ERRO após {duration:.1f}s: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restaurar a função original
        scraping_module._create_chrome_driver = original_create_driver

if __name__ == "__main__":
    print("🚀 Iniciando teste de scraping SEM headless...")
    test_without_headless()
    print("\n🎉 Teste finalizado!")
