from app.database import engine
from app.models.Base import Base



def main():

    print("Conectando ao banco...")

    Base.metadata.create_all(engine)

    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    main()