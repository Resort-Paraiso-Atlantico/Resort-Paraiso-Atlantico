from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.ReservaSuite import ReservaSuite
from datetime import date


class ReservaSuiteRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(self, reserva_suite: ReservaSuite) -> ReservaSuite:
        self.db.add(reserva_suite)
        self.db.commit()
        self.db.refresh(reserva_suite)
        return reserva_suite

    def buscar_por_id(self, id: int) -> ReservaSuite | None:
        return self.db.get(ReservaSuite, id)

    def listar_por_reserva(self, id_reserva: int) -> list[ReservaSuite]:
        return (
            self.db.query(ReservaSuite)
            .options(joinedload(ReservaSuite.suite))
            .filter(ReservaSuite.id_reserva == id_reserva)
            .all()
        )

    def listar_por_suite(self, id_suite: int) -> list[ReservaSuite]:
        return (
            self.db.query(ReservaSuite)
            .filter(ReservaSuite.id_suite == id_suite)
            .all()
        )

    def buscar_vinculo_ativo_por_suite(self, id_suite: int) -> ReservaSuite | None:
        return (
            self.db.query(ReservaSuite)
            .filter(
                ReservaSuite.id_suite == id_suite,
                ReservaSuite.data_saida.is_(None),
            )
            .first()
        )

    def existe_conflito(
    self,
    id_suite: int,
    data_entrada: date,
    data_saida: date,
    excluir_id: int | None = None,
) -> bool:
        query = self.db.query(ReservaSuite).filter(ReservaSuite.id_suite == id_suite)
        if excluir_id is not None:
            query = query.filter(ReservaSuite.id != excluir_id)
        query = query.filter(
            ReservaSuite.data_entrada < data_saida,
            or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida > data_entrada),
        )
        return self.db.query(query.exists()).scalar()
    
    def atualizar(self, reserva_suite: ReservaSuite) -> ReservaSuite:
        self.db.commit()
        self.db.refresh(reserva_suite)
        return reserva_suite

    def listar_por_suite(self, id_suite: int):
        return (
            self.db.query(ReservaSuite)
            .filter(ReservaSuite.id_suite == id_suite)
            .order_by(ReservaSuite.data_entrada)
            .all()
        )