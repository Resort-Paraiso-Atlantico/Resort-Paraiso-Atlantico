from sqlalchemy.orm import Session, joinedload
from app.models.Reserva import Reserva
from datetime import date


class ReservaRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(self, reserva: Reserva) -> Reserva:
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return self.buscar_por_id(reserva.id_reserva) or reserva

    def listar_todas(self) -> list[Reserva]:
        return (
            self.db.query(Reserva)
            .options(
                joinedload(Reserva.hospede),
                joinedload(Reserva.reserva_suites)
            )
            .order_by(Reserva.id_reserva.desc())
            .all()
        )

    def buscar_por_id(self, id_reserva: int) -> Reserva | None:
        return (
            self.db.query(Reserva)
            .options(
                joinedload(Reserva.hospede),
                joinedload(Reserva.reserva_suites)
            )
            .filter(Reserva.id_reserva == id_reserva)
            .first()
        )

    def buscar_por_cpf(self, cpf: str) -> list[Reserva]:
        return (
            self.db.query(Reserva)
            .options(
                joinedload(Reserva.hospede),
                joinedload(Reserva.reserva_suites)
            )
            .filter(Reserva.cpf_hospede == cpf)
            .order_by(Reserva.id_reserva.desc())
            .all()
        )

    def atualizar(self, reserva: Reserva) -> Reserva:
        self.db.commit()
        self.db.refresh(reserva)
        return self.buscar_por_id(reserva.id_reserva) or reserva

    def deletar(self, reserva: Reserva) -> None:
        self.db.delete(reserva)
        self.db.commit()