"""
Script de inicialização do sistema.
Cria o usuário administrador padrão se ele não existir.

Uso:
    python scripts/init_admin.py

Credenciais padrão:
    Email: admin@admin.com
    Senha: Senha@123
    Permissões: ADMIN (acesso total)
"""
import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from api.v1._database.models import Usuario
from api.utils.db_services import get_db
from api.utils.security import get_password_hash


def create_admin_user(db: Session):
    """
    Cria o usuário administrador padrão se ele não existir.
    
    Args:
        db: Sessão do banco de dados
    """
    # Dados do administrador padrão
    ADMIN_EMAIL = "admin@admin.com"
    ADMIN_NAME = "Admin"
    ADMIN_PASSWORD = "Senha@123"
    ADMIN_PERMISSIONS = ["ADMIN"]
    
    try:
        # Verificar se já existe um usuário com este email
        existing_admin = db.query(Usuario).filter(Usuario.email == ADMIN_EMAIL).first()
        
        if existing_admin:
            print(f"✅ Usuário administrador já existe:")
            print(f"   - Email: {existing_admin.email}")
            print(f"   - Nome: {existing_admin.nome}")
            print(f"   - Permissões: {existing_admin.permissoes}")
            print(f"   - Ativo: {existing_admin.flg_ativo}")
            
            # Verificar se precisa atualizar permissões
            if "ADMIN" not in (existing_admin.permissoes or []):
                print(f"\n⚠️  Usuário existe mas não tem permissão ADMIN. Atualizando...")
                existing_admin.permissoes = ADMIN_PERMISSIONS
                db.commit()
                db.refresh(existing_admin)
                print(f"✅ Permissões atualizadas para: {existing_admin.permissoes}")
            
            # Verificar se está desativado
            if not existing_admin.flg_ativo:
                print(f"\n⚠️  Usuário estava desativado. Reativando...")
                existing_admin.flg_ativo = True
                db.commit()
                db.refresh(existing_admin)
                print(f"✅ Usuário reativado com sucesso!")
            
            return existing_admin
        
        # Criar novo usuário administrador
        print("🔧 Criando usuário administrador padrão...")
        print(f"   - Email: {ADMIN_EMAIL}")
        print(f"   - Nome: {ADMIN_NAME}")
        print(f"   - Permissões: {ADMIN_PERMISSIONS}")
        
        # Hash da senha
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        
        # Criar usuário
        admin_user = Usuario(
            nome=ADMIN_NAME,
            email=ADMIN_EMAIL,
            senha=hashed_password,
            permissoes=ADMIN_PERMISSIONS,
            flg_ativo=True,
            flg_excluido=False
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Usuário administrador criado com sucesso!")
        print(f"\n📋 Credenciais de acesso:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Senha: {ADMIN_PASSWORD}")
        print(f"   Permissões: {ADMIN_PERMISSIONS}")
        print(f"\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
        return admin_user
        
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário administrador: {e}")
        db.rollback()
        raise


def main():
    """Função principal do script."""
    print("=" * 60)
    print("🚀 INICIALIZAÇÃO DO SISTEMA")
    print("=" * 60)
    print()
    
    try:
        # Obter sessão do banco de dados
        db = next(get_db())
        
        # Criar usuário administrador
        admin_user = create_admin_user(db)
        
        print()
        print("=" * 60)
        print("✅ Inicialização concluída com sucesso!")
        print("=" * 60)
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Erro durante a inicialização: {e}")
        print("=" * 60)
        print()
        return 1
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    exit(main())

