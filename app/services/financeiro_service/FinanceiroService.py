from datetime import date
from dataclasses import dataclass, field

from app.services.ReservaService import ReservaService
from app.services.pedido_service.PedidoCompraService import PedidoCompraService


# Status de Reserva que representam receita confirmada / realizada
STATUS_RESERVA_RECEITA = ("Confirmada", "Check-in", "Check-out", "Hospedado", "Finalizada")

# Status de Pedido de Compra que representam despesa efetiva (exclui cancelados)
STATUS_PEDIDO_DESPESA_EXCLUIDOS = ("CANCELADO", "Cancelado")


@dataclass
class ResumoFinanceiro:
    total_receitas: float = 0.0
    total_despesas: float = 0.0
    saldo: float = 0.0
    margem_lucro: float = 0.0
    ticket_medio_reserva: float = 0.0

    receitas_pendentes: float = 0.0
    despesas_pendentes: float = 0.0

    qtd_reservas_receita: int = 0
    qtd_pedidos_despesa: int = 0

    receitas_por_mes: dict = field(default_factory=dict)
    despesas_por_mes: dict = field(default_factory=dict)
    receitas_por_status: dict = field(default_factory=dict)
    despesas_por_status: dict = field(default_factory=dict)


class FinanceiroService:
    """
    Agrega dados financeiros a partir dos módulos de Reservas (receitas)
    e Pedidos de Compra (despesas) para geração de relatórios e dashboards executivos.
    """

    def __init__(self, db):
        self.reserva_service = ReservaService(db)
        self.pedido_service = PedidoCompraService(db)

    def _chave_mes(self, d: date) -> str:
        return d.strftime("%Y-%m") if d else "Sem Data"

    def obter_resumo(self) -> ResumoFinanceiro:
        reservas = self.reserva_service.listar_reservas()
        pedidos = self.pedido_service.listar_todos()

        resumo = ResumoFinanceiro()

        for r in reservas:
            valor = float(r.valor_total or 0.0)
            st_norm = (r.status or "").strip()

            if st_norm in STATUS_RESERVA_RECEITA:
                resumo.total_receitas += valor
                resumo.qtd_reservas_receita += 1
                resumo.receitas_por_status[st_norm] = resumo.receitas_por_status.get(st_norm, 0.0) + valor
                if r.data_reserva:
                    mes = self._chave_mes(r.data_reserva)
                    resumo.receitas_por_mes[mes] = resumo.receitas_por_mes.get(mes, 0.0) + valor
            elif st_norm == "Pendente":
                resumo.receitas_pendentes += valor

        for p in pedidos:
            valor = float(p.valor_total or 0.0)
            st_norm = (p.status or "").strip()

            if st_norm in STATUS_PEDIDO_DESPESA_EXCLUIDOS:
                continue

            resumo.total_despesas += valor
            resumo.qtd_pedidos_despesa += 1
            resumo.despesas_por_status[st_norm] = resumo.despesas_por_status.get(st_norm, 0.0) + valor

            if p.data_pedido:
                mes = self._chave_mes(p.data_pedido)
                resumo.despesas_por_mes[mes] = resumo.despesas_por_mes.get(mes, 0.0) + valor

            if st_norm.upper() == "PENDENTE":
                resumo.despesas_pendentes += valor

        resumo.saldo = resumo.total_receitas - resumo.total_despesas
        if resumo.total_receitas > 0:
            resumo.margem_lucro = (resumo.saldo / resumo.total_receitas) * 100.0
        if resumo.qtd_reservas_receita > 0:
            resumo.ticket_medio_reserva = resumo.total_receitas / resumo.qtd_reservas_receita

        return resumo

    def listar_receitas(self):
        """Reservas com status que geram receita, ordenadas da mais recente."""
        reservas = self.reserva_service.listar_reservas()
        receitas = [r for r in reservas if (r.status or "").strip() in STATUS_RESERVA_RECEITA and r.valor_total]
        return sorted(receitas, key=lambda r: r.data_reserva or date.min, reverse=True)

    def listar_despesas(self):
        """Pedidos de compra que geram despesa, ordenados do mais recente."""
        pedidos = self.pedido_service.listar_todos()
        despesas = [p for p in pedidos if (p.status or "").strip() not in STATUS_PEDIDO_DESPESA_EXCLUIDOS]
        return sorted(despesas, key=lambda p: p.data_pedido or date.min, reverse=True)
