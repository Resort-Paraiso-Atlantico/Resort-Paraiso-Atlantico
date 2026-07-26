from sqlalchemy.orm import Session

from app.models.fornecedor.Fornecedor import Fornecedor
from app.repositories.fornecedor_repository.FornecedorRepository import FornecedorRepository


class FornecedorService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = FornecedorRepository(db)

    def criar_fornecedor(
        self,
        cnpj: str,
        nome: str,
        telefone: str,
        email: str,
        endereco: str
        ):
        if self.buscar_por_cnpj(cnpj):
            raise ValueError("Cnpj já está cadastrado.")

        fornecedor = Fornecedor(
            cnpj = cnpj,
            nome = nome,
            telefone = telefone,
            email = email,
            endereco = endereco
        )
        return self.repository.criar_fornecedor(fornecedor)

    def buscar_por_cnpj(self, cnpj: str):
        if not cnpj:
            raise ValueError("Cnpj vazio.")
        return self.repository.buscar_por_cnpj(cnpj)

    def buscar_por_nome(self, nome: str):
        if not nome:
            raise ValueError("Nome vazio.")
        return self.repository.buscar_por_nome(nome)

    def listar_fornecedores(self):
        return self.repository.listar_todos()

    def atualizar_fornecedor(
        self,
        cnpj: str,
        nome: str,
        telefone: str,
        email: str,
        endereco: str
        ) -> Fornecedor:
        fornecedor = self.repository.buscar_por_cnpj(cnpj)
        if fornecedor is None:
            raise ValueError("Fornecedor não encontrado.")
        fornecedor.nome = nome
        fornecedor.telefone = telefone
        fornecedor.email = email
        fornecedor.endereco = endereco
        return self.repository.atualizar(fornecedor)

    def remover_fornecedor(self, cnpj: str):
        if not cnpj:
            raise ValueError("CNPJ inválido.")

        fornecedor = self.repository.buscar_por_cnpj(cnpj)
        if fornecedor is None:
            raise ValueError("Fornecedor não encontrado.")
    
        removido = self.repository.remover(cnpj)
        if not removido:
            raise ValueError("Hóspode não encontrado.")
        return removido
    