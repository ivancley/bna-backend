#!/usr/bin/env python
"""
Script para testar se a task pode ser importada corretamente.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Testa a importação da task."""
    
    print("=" * 70)
    print("🧪 TESTANDO IMPORTAÇÃO DA TASK")
    print("=" * 70)
    
    try:
        print("\n1️⃣ Importando celery_app...")
        from api.utils.celery_app import celery_app
        print("   ✅ celery_app importado com sucesso")
        
        print("\n2️⃣ Importando scrape_url_task...")
        from api.v1.web_link.celery.tasks import scrape_url_task
        print("   ✅ scrape_url_task importado com sucesso")
        
        print(f"\n3️⃣ Nome da task: {scrape_url_task.name}")
        
        print("\n4️⃣ Verificando se está registrada no celery_app...")
        if scrape_url_task.name in celery_app.tasks:
            print(f"   ✅ Task '{scrape_url_task.name}' está registrada!")
        else:
            print(f"   ❌ Task '{scrape_url_task.name}' NÃO está registrada!")
            print("\n   Tasks disponíveis:")
            for task_name in sorted(celery_app.tasks.keys()):
                if 'web_link' in task_name or 'scrape' in task_name:
                    print(f"      - {task_name}")
        
        print("\n5️⃣ Testando chamada da task (sem executar)...")
        # Apenas verifica se pode criar a signature
        signature = scrape_url_task.s("test-id", "http://example.com")
        print(f"   ✅ Signature criada: {signature}")
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()

