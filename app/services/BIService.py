from datetime import datetime
from datetime import date
from sqlalchemy.orm import Session
from collections import defaultdict

from app.repositories.BIRepository import BIRepository
class BIService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BIRepository(db)

    #suites
    # Taxa de ocupação hoje
    def suites_ocupadas_hoje(self,tipo: str | None = None):
        suites_ocupadas = self.repository.suites_ocupadas_hoje(tipo) #se for nenhuma, retorna todos. Se for algum tipo, retorna só o do tipo 
        suites_total = self.repository.quantidade_suites(tipo)

        if suites_total == 0:
            return 0.0

        return (suites_ocupadas/suites_total) * 100
    
    # Taxa média de ocupação no período
    def suites_ocupadas_periodo(self,data_inicio:date, data_fim:date, tipo: str | None=None):
        if data_inicio is None or data_fim is None:
            raise ValueError("Data inicio e data fim devem ser preenchidos.") 
        if data_inicio > data_fim :
            raise ValueError("A data de inicio deve ser anterior a data final")
        if data_inicio == data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final. Se quiser para hoje use suites ocupadas hoje!")

        suites_ocupadas = self.repository.suites_ocupadas_periodo(data_inicio,data_fim,tipo)
        suites_total = self.repository.quantidade_suites(tipo)

        #quantos dias tem esse periodo
        dias = (data_fim - data_inicio).days
        if dias <= 0:
            dias = 1


        if suites_total == 0:
            return 0.0
        
        return (suites_ocupadas/(suites_total*dias)) * 100
    
    #Suites mais utilizadas
    def suites_mais_utilizadas(self, data_inicio: date | None = None, data_fim: date | None = None, tipo: str | None = None):
        if (data_inicio is None) != (data_fim is None):
            raise ValueError("Data inicio e data fim devem ser preenchidos juntos, ou nenhum dos dois.")
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final")
        if data_inicio is not None and data_fim is not None and data_inicio == data_fim:
            raise ValueError("O intervalo não pode ter data_inicio igual a data_fim.")

        resultado = self.repository.suites_mais_utilizadas(data_inicio, data_fim, tipo)

        return [{"suite": suite, "qtd_reservas": qtd} for suite, qtd in resultado]
    # Número de hóspedes

    # Quantas suites estão disponiveis/ em limpeza / em manutenção AGORA
    def distribuicao_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_por_status()

    # quantas suites de cada tipo tem
    def composicao_por_tipo(self) -> dict[str, int]:
        return self.repository.distribuicao_por_tipo()

    # manda a taxa de ocupacao de CADa tipo
    def ocupacao_por_tipo(self, data_inicio: date, data_fim: date) -> dict[str, float]:
        if data_inicio is None or data_fim is None:
            raise ValueError("Data inicio e data fim devem ser preenchidos.")
        if data_inicio > data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final")
        if data_inicio == data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final. O intervalo não pode ser de um único dia com data_fim igual a data_inicio.")

        dias = (data_fim - data_inicio).days
        if dias <= 0:
            dias = 1

        dias_ocupados_por_tipo = self.repository.ocupacao_por_tipo_periodo(data_inicio, data_fim)
        total_por_tipo = self.repository.distribuicao_por_tipo()

        resultado = {}
        for tipo, total_suites in total_por_tipo.items():
            ocupados = dias_ocupados_por_tipo.get(tipo, 0)
            resultado[tipo] = (ocupados / (total_suites * dias)) * 100 if total_suites > 0 else 0.0

        return resultado
    # Número de reservas
    # Faturamento total
    # Ticket médio por reserva
    # Número de suítes disponíveis
    # Número de suítes ocupadas
    # Número de suítes em manutenção
    # Solicitações abertas
    # Solicitações pendentes de limpeza
    #eventos

    # taxa de ocupação de um evento específico
    def evento_taxa_ocupacao(self, id_evento: int) -> float:
        dados = self.repository.evento_capacidade_inscritos(id_evento)
        if dados is None:
            raise ValueError("Evento não encontrado.")
        capacidade, inscritos = dados
        return (inscritos / capacidade) * 100 if capacidade > 0 else 0.0

    # eventos mais procurados
    def eventos_mais_procurados(self, data_inicio: datetime | None = None, data_fim: datetime | None = None):
        if (data_inicio is None) != (data_fim is None):
            raise ValueError("Data inicio e data fim devem ser preenchidos juntos, ou nenhum dos dois.")
        if data_inicio is not None and data_fim is not None and data_inicio == data_fim:
            raise ValueError("O intervalo não pode ter data_inicio igual a data_fim.")
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final.")

        resultado = self.repository.eventos_mais_procurados(data_inicio, data_fim)
        return [{"evento": evento, "qtd_inscricoes": qtd} for evento, qtd in resultado]

    # ocupação média dos eventos no período
    def ocupacao_media_eventos_periodo(self, data_inicio: datetime, data_fim: datetime) -> float:
        if data_inicio is None or data_fim is None:
            raise ValueError("Data inicio e data fim devem ser preenchidos.")
        if data_inicio == data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final.")
        if data_inicio > data_fim:
            raise ValueError("A data de inicio deve ser anterior a data final.")

        eventos = self.repository.eventos_periodo_com_inscritos(data_inicio, data_fim)
        if not eventos:
            return 0.0

        taxas = [(qtd / evento.capacidade) * 100 if evento.capacidade > 0 else 0.0 for evento, qtd in eventos]
        return sum(taxas) / len(taxas)

    # lead time médio de inscrição, em dias
    def lead_time_medio_inscricao(self) -> float:
        inscricoes = self.repository.inscricoes_com_evento()
        diffs = [
            (i.evento.inicio_evento - i.data_inscricao).days
            for i in inscricoes
            if i.data_inscricao is not None
        ]
        return sum(diffs) / len(diffs) if diffs else 0.0

    # distribuição por status
    def distribuicao_eventos_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_eventos_por_status()

    # volume de eventos por mês
    def eventos_por_mes(self) -> dict[str, int]:
        eventos = self.repository.listar_eventos_com_data()
        contagem = defaultdict(int)
        for e in eventos:
            chave = e.inicio_evento.strftime("%Y-%m")
            contagem[chave] += 1
        return dict(contagem)
    #reservas
    # conta as reservas
    def reservas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes()

    #conta as reservas canceladas
    def reservas_canceladas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes(status="Cancelada")

    # conta as reservas concluidas
    def reservas_concluidas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes(status="Finalizada")

    # contas as reservas pendentes ou confirmadas
    def reservas_futuras(self) -> int:
        return self.repository.contar_reservas_futuras()
    
    # calcula a duracao media das reservas
    def duracao_media_reservas(self) -> float:
        return self.repository.duracao_media_reservas_realizada()

    
        # % de reservas canceladas sobre o total histórico
    def taxa_cancelamento_reservas(self) -> float:
        canceladas, total = self.repository.taxa_cancelamento_reservas()
        return (canceladas / total) * 100 if total > 0 else 0.0

    # atxa e atraso médio de check-in em relação ao previsto
    def taxa_atraso_checkin(self) -> dict[str, float]:
        reservas = self.repository.reservas_com_checkin_realizado()
        if not reservas:
            return {"taxa_atraso": 0.0, "atraso_medio_dias": 0.0}

        atrasadas = [r for r in reservas if r.checkin_realizado > r.checkin_previsto]
        taxa = (len(atrasadas) / len(reservas)) * 100
        atraso_medio = (
            sum((r.checkin_realizado - r.checkin_previsto).days for r in atrasadas) / len(atrasadas)
            if atrasadas else 0.0
        )
        return {"taxa_atraso": taxa, "atraso_medio_dias": atraso_medio}

    # Quantas reservas estão em cada status AGORA
    def distribuicao_reservas_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_reservas_por_status()

    #chamados


    # Tempo médio de conclusão de chamado, em dias
    def tempo_medio_conclusao_chamado(self) -> float:
        chamados = self.repository.chamados_concluidos()
        if not chamados:
            return 0.0
        duracoes = [(c.data_conclusao - c.data_abertura).days for c in chamados]
        return sum(duracoes) / len(duracoes)

    # Chamados agrupados pelo tipo de suíte de origem
    def chamados_por_tipo_suite(self) -> dict[str, int]:
        return self.repository.chamados_por_tipo_suite()

    # Quantidade total de chamados por tipo (Limpeza/Manutenção)
    def quantidade_por_tipo_chamado(self) -> dict[str, int]:
        return self.repository.quantidade_por_tipo_chamado()

    # Quantos chamados estão em cada status agora
    def distribuicao_chamados_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_chamados_por_status()

    # Quantos chamados existem em cada prioridade
    def distribuicao_chamados_por_prioridade(self) -> dict[str, int]:
        return self.repository.distribuicao_chamados_por_prioridade()

    # % de chamados cancelados sobre o total histórico
    def taxa_cancelamento_chamados(self) -> float:
        cancelados, total = self.repository.taxa_cancelamento_chamados()
        return (cancelados / total) * 100 if total > 0 else 0.0

    # Ranking de suítes com mais chamados abertos ao longo do tempo
    def suites_mais_chamados(self, limite: int = 10):
        resultado = self.repository.suites_mais_chamados(limite)
        return [{"suite": suite, "qtd_chamados": qtd} for suite, qtd in resultado]

    # ---------- hóspedes ----------

    # Cadastros de hóspedes por mês
    def cadastros_hospedes_por_mes(self) -> dict[str, int]:
        hospedes = self.repository.listar_hospedes_com_cadastro()
        contagem = defaultdict(int)
        for h in hospedes:
            contagem[h.data_cadastro.strftime("%Y-%m")] += 1
        return dict(contagem)

    # Mês com mais cadastros de hóspedes
    def mes_com_mais_cadastros(self) -> tuple[str, int] | None:
        por_mes = self.cadastros_hospedes_por_mes()
        if not por_mes:
            return None
        return max(por_mes.items(), key=lambda item: item[1])

    # Hóspedes com mais de uma reserva (recorrentes)
    def hospedes_recorrentes(self):
        resultado = self.repository.hospedes_com_multiplas_reservas()
        return [{"hospede": hospede, "qtd_reservas": qtd} for hospede, qtd in resultado]
    
    