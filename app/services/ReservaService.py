from datetime import date
from sqlalchemy.orm import Session
from app.models.Reserva import Reserva
from app.repositories.ReservaRepository import ReservaRepository


class ReservaService:

    #fazendo o repository
    def __init__(self, db: Session):
        self.repository = ReservaRepository(db)

    def criar_reserva(
        self,
        cpf_hospede: str,
        checkin_previsto: date,
        checkout_previsto: date,
        status: str = "Pendente"):
        if checkin_previsto >= checkout_previsto:
            raise ValueError("A data de check-in deve ser anterior ao check-out.")

        reserva = Reserva(
            cpf_hospede=cpf_hospede,
            data_reserva=date.today(),
            checkin_previsto=checkin_previsto,
            checkout_previsto=checkout_previsto,
            status=status,
        )
        return self.repository.criar(reserva)

    def listar_reservas(self) -> list[Reserva]:
        return self.repository.listar_todas()

    def buscar_por_cpf(self, cpf: str) -> list[Reserva]:
        return self.repository.buscar_por_cpf(cpf)

    def cancelar_reserva(self, id_reserva: int) -> Reserva:
        reserva = self.repository.buscar_por_id(id_reserva)
        if not reserva:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")
        if reserva.status == "Cancelada":
            raise ValueError("Reserva já está cancelada.")
        reserva.status = "Cancelada"
        return self.repository.atualizar(reserva)