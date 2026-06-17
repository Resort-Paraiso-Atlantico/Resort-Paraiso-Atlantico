from database import engine

from models.Base import Base

# IMPORTANTE:
# importa o model para o SQLAlchemy registrá-lo
from models import Hospede


def main():

    print("Conectando ao banco...")

    Base.metadata.create_all(engine)

    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    main()