from app.models.Suite import Suite
from app.database import SessionLocal

def criar_suite(numero: int ,tipo: str , capacidade:int,valor_diaria: float,status: str):

    

    try:
        suite = Suite(
        numero= numero,
        tipo=tipo,
        capacidade=capacidade,
        valor_diaria=valor_diaria,
        status=status,
        )

        db = SessionLocal()

        db.add(suite)
        db.commit()
        db.refresh(suite)

        return suite
    
    except Exception:
        db.rollback()
        raise

    finally:
        #tem q lembrar de fechar SEMPRE o sessionLocal
        db.close()