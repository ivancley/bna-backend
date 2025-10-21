#!/usr/bin/env python
"""
Script para verificar quais tasks estão registradas no Celery.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.utils.celery_app import celery_app

def main():
    """Lista todas as tasks registradas no Celery."""
    
    print("=" * 70)
    print("📋 TASKS REGISTRADAS NO CELERY")
    print("=" * 70)
    
    # Lista todas as tasks
    all_tasks = sorted(celery_app.tasks.keys())
    
    # Filtra tasks do sistema
    user_tasks = [t for t in all_tasks if not t.startswith('celery.')]
    
    if not user_tasks:
        print("\n❌ NENHUMA task de usuário registrada!")
        print("\n💡 Certifique-se de que:")
        print("   1. O módulo está no 'include' do celery_app")
        print("   2. O decorator @celery_app.task está correto")
        print("   3. Não há erros de importação")
        return
    
    print(f"\n✅ Total de tasks registradas: {len(user_tasks)}\n")
    
    # Agrupa por tipo
    email_tasks = [t for t in user_tasks if 'email' in t]
    scraping_tasks = [t for t in user_tasks if 'web_link' in t or 'scraping' in t]
    other_tasks = [t for t in user_tasks if t not in email_tasks and t not in scraping_tasks]
    
    if email_tasks:
        print("📧 EMAIL TASKS:")
        for task in email_tasks:
            print(f"   - {task}")
        print()
    
    if scraping_tasks:
        print("🔍 WEB SCRAPING TASKS:")
        for task in scraping_tasks:
            print(f"   - {task}")
        print()
    
    if other_tasks:
        print("📦 OUTRAS TASKS:")
        for task in other_tasks:
            print(f"   - {task}")
        print()
    
    # Verifica configuração de rotas
    print("=" * 70)
    print("🗺️  CONFIGURAÇÃO DE ROTAS")
    print("=" * 70)
    
    routes = celery_app.conf.task_routes
    if routes:
        for pattern, config in routes.items():
            print(f"   {pattern} → fila '{config.get('queue', 'default')}'")
    else:
        print("   ⚠️  Nenhuma rota configurada")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

