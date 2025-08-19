import logging
# --- INÍCIO DA CORREÇÃO ---
# Importamos o modelo explicitamente para que o SQLAlchemy o reconheça
from app.models import EngineData
# --- FIM DA CORREÇÃO ---
from app.database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Criando/Atualizando tabelas no banco de dados...")
    try:
        # Agora que o modelo foi importado, o Base.metadata sabe da nova coluna
        # e o SQLAlchemy irá adicionar a coluna que falta.
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas/atualizadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar/atualizar tabelas: {e}")

if __name__ == "__main__":
    init_db()