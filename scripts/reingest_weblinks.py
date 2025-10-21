#!/usr/bin/env python
"""
Script para re-ingerir todos os WebLinks existentes.
Usado após corrigir o formato de embeddings no banco.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.v1._database.models import WebLink
from api.utils.settings import settings
from api.v1.web_link.celery.tasks import scrape_url_task

def main():
    """Re-ingere todos os WebLinks que possuem URL."""
    
    # Cria sessão do banco
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Busca todos os WebLinks com URL
        weblinks = db.query(WebLink).filter(
            WebLink.weblink.isnot(None),
            WebLink.flg_excluido == False
        ).all()
        
        print(f"📊 Encontrados {len(weblinks)} WebLinks para re-ingerir")
        
        if not weblinks:
            print("✅ Nenhum WebLink para processar")
            return
        
        # Confirma antes de prosseguir
        resposta = input(f"\n⚠️  Deseja re-ingerir {len(weblinks)} WebLinks? (sim/não): ")
        if resposta.lower() not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada")
            return
        
        # Dispara tasks para cada WebLink
        dispatched = 0
        for weblink in weblinks:
            try:
                scrape_url_task.delay(str(weblink.id), weblink.weblink)
                print(f"✅ Task disparada para: {weblink.weblink}")
                dispatched += 1
            except Exception as e:
                print(f"❌ Erro ao disparar task para {weblink.weblink}: {e}")
        
        print(f"\n🎯 Total de tasks disparadas: {dispatched}/{len(weblinks)}")
        print("⏳ Aguarde as tasks serem processadas pelo Celery worker...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

