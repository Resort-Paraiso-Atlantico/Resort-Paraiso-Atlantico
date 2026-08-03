from datetime import date
from dataclasses import dataclass, field

from app.services.ReservaService import ReservaService
from app.services.pedido_service.PedidoCompraService import PedidoCompraService


# Status de Reserva que representam receita já confirmada/realizada.
# "Pendente" fica de fora: ainda não houve confirmação de pagamento.
STATUS_RESERVA_RECEITA = ("Confirmada", "Hospedado", "Finalizada")

# Status de Pedido de Compra que representam despesa efetiva.
# "CANCELADO" fica de fora do total de despesas.
STATUS_PEDIDO_DESPESA_EXCLUIDOS = ("CANCELADO",)


@dataclass
class ResumoFinanceiro:
    total_receitas: float = 0.0
    total_despesas: float = 0.0
    saldo: float = 0.0

    receitas_pendentes: float = 0.0
    despesas_pendentes: float = 0.0

    qtd_reservas_receita: int = 0
    qtd_pedidos_despesa: int = 0

    receitas_por_mes: dict = field(default_factory=dict)
    despesas_por_mes: dict = field(default_factory=dict)


class FinanceiroService:
    """
    Agrega dados financeiros a partir de módulos já existentes
    (Reservas = receita, Pedidos de Compra = despesa), sem criar
    uma tabela própria. É um serviço somente leitura.
    """

    def __init__(self, db):
        self.reserva_service = ReservaService(db)
        self.pedido_service = PedidoCompraService(db)

    def _chave_mes(self, d: date) -> str:
        return d.strftime("%Y-%m")

    def obter_resumo(self) -> ResumoFinanceiro:
        reservas = self.reserva_service.listar_reservas()
        pedidos = self.pedido_service.listar_todos()

        resumo = ResumoFinanceiro()

        for r in reservas:
            valor = r.valor_total or 0.0
            if r.status in STATUS_RESERVA_RECEITA:
                resumo.total_receitas += valor
                resumo.qtd_reservas_receita += 1
                if r.data_reserva:
                    mes = self._chave_mes(r.data_reserva)
                    resumo.receitas_por_mes[mes] = resumo.receitas_por_mes.get(mes, 0.0) + valor
            elif r.status == "Pendente":
                resumo.receitas_pendentes += valor

        for p in pedidos:
            valor = p.valor_total or 0.0
            if p.status in STATUS_PEDIDO_DESPESA_EXCLUIDOS:
                continue
            resumo.total_despesas += valor
            resumo.qtd_pedidos_despesa += 1
            if p.data_pedido:
                mes = self._chave_mes(p.data_pedido)
                resumo.despesas_por_mes[mes] = resumo.despesas_por_mes.get(mes, 0.0) + valor
            if p.status == "PENDENTE":
                resumo.despesas_pendentes += valor

        resumo.saldo = resumo.total_receitas - resumo.total_despesas
        return resumo

    def listar_receitas(self):
        """Reservas com status que geram receita, ordenadas da mais recente."""
        reservas = self.reserva_service.listar_reservas()
        receitas = [r for r in reservas if r.status in STATUS_RESERVA_RECEITA and r.valor_total]
        return sorted(receitas, key=lambda r: r.data_reserva or date.min, reverse=True)

    def listar_despesas(self):
        """Pedidos de compra que geram despesa, ordenados do mais recente."""
        pedidos = self.pedido_service.listar_todos()
        despesas = [p for p in pedidos if p.status not in STATUS_PEDIDO_DESPESA_EXCLUIDOS]
        return sorted(despesas, key=lambda p: p.data_pedido or date.min, reverse=True)
