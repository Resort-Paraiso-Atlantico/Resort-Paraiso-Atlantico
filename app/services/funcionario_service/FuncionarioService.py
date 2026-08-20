from app.models.funcionario.Funcionario import Funcionario
from app.repositories.funcionario_repository.FuncionarioRepository import FuncionarioRepository
from sqlalchemy.orm import Session


class FuncionarioService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = FuncionarioRepository(db)

    def criar_funcionario(
        self,
        cpf_funcionario: str,
        nome: str,
        telefone: str,
        email: str,
        cargo: str,
        salario: float
    ):
        if self.buscar_por_cpf(cpf_funcionario):
            raise ValueError("CPF já cadastrado.")
        if salario <= 0:
            raise ValueError("Salário deve ser um valor positivo.")

        funcionario = Funcionario(
            cpf_funcionario = cpf_funcionario,
            nome = nome,
            telefone = telefone,
            email = email,
            cargo = cargo,
            salario = salario
        )
        return self.repository.criar_funcionario(funcionario)

    def buscar_por_cpf(self, cpf: str) -> Funcionario | None:
        if not cpf:
            raise ValueError("CPF inválido.")
        return self.repository.buscar_por_cpf(cpf)
    
    def listar_funcionarios(self):
        return self.repository.listar_funcionarios

    def atualizar_funcionario(
        self,
        cpf_funcionario: str,
        nome,
        telefone: str,
        email: str,
        cargo: str,
        salario: float,
    ) -> Funcionario:
        funcionario = self.repository.buscar_por_cpf(cpf_funcionario)

        if funcionario is None:
            raise ValueError("Funcionario não encontrado.")
        if salario <= 0:
            raise ValueError("Salário deve ser um valor positivo.")

        funcionario.nome = nome
        funcionario.telefone = telefone
        funcionario.email = email
        funcionario.cargo = cargo
        funcionario.salario = salario

        return self.repository.atualizar(funcionario)

    def remover_funcionario(self, cpf: str):
        if not cpf:
            raise ValueError("CPF inválido.")

        funcionario = self.repository.buscar_por_cpf(cpf)
        if funcionario is None:
            raise ValueError("Funcionario não encontrado.")

        removido = self.repository.remover(cpf)
        if not removido:
            raise ValueError("Funcionario não encontrado.")
        return removido
        


        
