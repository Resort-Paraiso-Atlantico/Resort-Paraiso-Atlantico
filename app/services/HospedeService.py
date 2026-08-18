from datetime import date
from sqlalchemy.orm import Session
from app.models.Hospede import Hospede
from app.repositories.HospedeRepository import HospedeRepository
from app.services.ReservaService import ReservaService
from app.services.HospedeEventoService import HospedeEventoService

class HospedeService:

    #fazendo o repository
    def __init__(self, db: Session):
        self.db = db
        self.repository = HospedeRepository(db)
        self.hospede_evento_service = HospedeEventoService(self.db)

    def criar_hospede(
        self,
        cpf: str,
        nome:str,
        telefone:str,
        email:str,
        endereco:str
        ):
        if self.buscar_por_cpf(cpf):
            raise ValueError("Cpf ja está cadastrado")
        if self.buscar_por_email(email):
                    raise ValueError("Email ja está sendo usado")

        hospede = Hospede(cpf=cpf,nome=nome,telefone=telefone,email=email,endereco=endereco)
        return self.repository.criar(hospede)
    
    def buscar_por_cpf(self, cpf: str):
        if not cpf:
            raise ValueError("Cpf vazio")
        return self.repository.buscar_por_cpf(cpf)
    
    def buscar_por_email(self, email: str):
        if not email:
            raise ValueError("Email vazio")
        return self.repository.buscar_por_email(email)
    
    def listar_hospedes(self):
        return self.repository.listar_todos()
    
    def atualizar_hospede(self,cpf: str, nome: str, telefone: str, email: str, endereco: str) -> Hospede:
        hospede = self.repository.buscar_por_cpf(cpf)
        if hospede is None:
            raise ValueError("Hóspede não encontrado")
        hospede.nome = nome
        hospede.telefone = telefone
        hospede.email = email
        hospede.endereco = endereco
        return self.repository.atualizar(hospede)
    
    def remover_hospede(self, cpf: str):
        if not cpf:
            raise ValueError("CPF inválido")
        
        hospede = self.repository.buscar_por_cpf(cpf)
        if hospede is None: 
            raise ValueError("Hóspede não encontrado")

        reserva_service = ReservaService(self.db)
        reservas = reserva_service.buscar_por_cpf(cpf)
        if reservas:
            raise ValueError(
                "Não é possível remover um hóspede com reservas cadastradas."
            )

        inscricoes = self.hospede_evento_service.listar_eventos_por_hospede(cpf)
        if inscricoes:
            raise ValueError("Não é possível remover um hóspede com inscrições em eventos.")
        
        removido = self.repository.remover(cpf)
        if not removido:
            raise ValueError("Hóspede não encontrado")
        
        return removido