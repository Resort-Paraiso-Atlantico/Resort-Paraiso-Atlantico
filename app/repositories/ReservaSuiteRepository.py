from sqlalchemy.orm import Session, joinedload
from app.models.ReservaSuite import ReservaSuite


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

    def atualizar(self, reserva_suite: ReservaSuite) -> ReservaSuite:
        self.db.commit()
        self.db.refresh(reserva_suite)
        return reserva_suite