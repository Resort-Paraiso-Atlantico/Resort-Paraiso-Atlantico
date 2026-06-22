from sqlalchemy.orm import Session
from app.models.Reserva import Reserva
from datetime import date


class ReservaRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(self, reserva: Reserva) -> Reserva:
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def listar_todas(self) -> list[Reserva]:
        return self.db.query(Reserva).all()

    def buscar_por_id(self, id_reserva: int) -> Reserva | None:
        return self.db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()

    def buscar_por_cpf(self, cpf: str) -> list[Reserva]:
        return self.db.query(Reserva).filter(Reserva.cpf_hospede == cpf).all()

    def atualizar(self, reserva: Reserva) -> Reserva:
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def deletar(self, reserva: Reserva) -> None:
        self.db.delete(reserva)
        self.db.commit()