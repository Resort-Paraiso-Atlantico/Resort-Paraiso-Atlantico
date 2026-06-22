from app.database import engine
from app.models.Base import Base
from app.pages.TesteSuite import form_criar_suite


def main():

    

    
    print("Conectando ao banco...")

    Base.metadata.create_all(engine)

    print("Tabelas criadas com sucesso!")
    form_criar_suite()

if __name__ == "__main__":
    main()