#!/usr/bin/env python
"""
Script para limpar todos os conhecimentos do banco.
Use antes de re-ingerir os WebLinks com formato correto de embeddings.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.utils.settings import settings

def main():
    """Limpa todos os conhecimentos do banco."""
    
    # Cria sessão do banco
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Conta conhecimentos atuais
        result = db.execute(text("SELECT COUNT(*) FROM conhecimento"))
        count = result.scalar()
        
        print(f"📊 Total de conhecimentos no banco: {count}")
        
        if count == 0:
            print("✅ Banco já está vazio")
            return
        
        # Confirma antes de deletar
        resposta = input(f"\n⚠️  Deseja deletar TODOS os {count} conhecimentos? (sim/não): ")
        if resposta.lower() not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada")
            return
        
        # Deleta todos os conhecimentos
        db.execute(text("DELETE FROM conhecimento"))
        db.commit()
        
        print("✅ Todos os conhecimentos foram deletados")
        print("\n💡 Próximo passo: Execute reingest_weblinks.py para re-ingerir os WebLinks")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

