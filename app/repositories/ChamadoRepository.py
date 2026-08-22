from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.Chamado import Chamado


class ChamadoRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def criar(self, chamado: Chamado) -> Chamado:
        self.db.add(chamado)
        self.db.commit()
        self.db.refresh(chamado)
        return chamado

    def buscar_por_id(self, id_chamado: int) -> Chamado | None:
        return self.db.get(Chamado, id_chamado)

    def atualizar(self, chamado: Chamado) -> Chamado:
        self.db.commit()
        self.db.refresh(chamado)
        return chamado

    # ── Listagens ─────────────────────────────────────────────────────────────

    def listar_pendentes(self, tipo: str | None = None) -> list[Chamado]:
        q = (
            select(Chamado)
            .options(joinedload(Chamado.suite))
            .where(Chamado.status == "Aberto")
        )
        if tipo:
            q = q.where(Chamado.tipo == tipo)
        return list(self.db.execute(q).scalars().all())

    def listar_por_suite(self, id_suite: int) -> list[Chamado]:
        q = (
            select(Chamado)
            .where(Chamado.id_suite == id_suite)
            .order_by(Chamado.data_abertura.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def listar_concluidos(self) -> list[Chamado]:
        q = (
            select(Chamado)
            .options(joinedload(Chamado.suite))
            .where(Chamado.status == "Concluido")
            .order_by(Chamado.data_conclusao.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def listar_cancelados(self) -> list[Chamado]:
        q = (
            select(Chamado)
            .options(joinedload(Chamado.suite))
            .where(Chamado.status == "Cancelado")
            .order_by(Chamado.data_conclusao.desc())
        )
        return list(self.db.execute(q).scalars().all())