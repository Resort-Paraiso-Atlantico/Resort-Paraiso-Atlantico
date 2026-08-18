from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.Chamado import Chamado
from app.repositories.ChamadoRepository import ChamadoRepository
from app.repositories.SuiteRepository import SuiteRepository


class ChamadoService:
    ORDEM_PRIORIDADE = {"Urgente": 0, "Alta": 1, "Média": 2, "Baixa": 3}

    def __init__(self, db: Session) -> Chamado:
            self.repository = ChamadoRepository(db)
            self.suite_repository = SuiteRepository(db)

    def abrir_chamado(self,id_suite:int,tipo:str,prioridade:str,descricao:str):
        # 1. Validação do ID da Suíte
        if id_suite is None:
            raise ValueError("ID da suíte é obrigatório.")

        # 2. Validação se a suíte existe no banco
        suite = self.suite_repository.buscar_por_id(id_suite)
        if not suite:
            raise ValueError(f"Suíte #{id_suite} não encontrada.")

        # 3. Validação do Tipo
        if not tipo or not tipo.strip():
            raise ValueError("O tipo do chamado é obrigatório.")
        
        tipos_validos = ("Limpeza", "Manutenção")
        if tipo.strip() not in tipos_validos:
            raise ValueError(f"Tipo inválido. Use um dos seguintes: {', '.join(tipos_validos)}.")

        # 4. Validação da Prioridade
        if not prioridade or not prioridade.strip():
            raise ValueError("A prioridade é obrigatória.")

        prioridades_validas = ("Baixa", "Média", "Alta", "Urgente")
        if prioridade.strip() not in prioridades_validas:
            raise ValueError(f"Prioridade inválida. Use uma das seguintes: {', '.join(prioridades_validas)}.")

        # 5. Validação da Descrição
        if not descricao or not descricao.strip():
            raise ValueError("A descrição do chamado é obrigatória.")


        chamado = Chamado(
            id_suite=id_suite,
            tipo=tipo.strip(), #Manutenção ou Limpeza
            prioridade=prioridade.strip(), # Baixa Media Alta Urgente
            status= "Aberto",
            data_abertura=datetime.now(),
            descricao=descricao.strip(),
        )
        suite.status = tipo.strip()
        self.suite_repository.atualizar(suite)

        return self.repository.criar(chamado)

    def concluir_chamado(self,id_chamado:int):
        if id_chamado is None:
            raise ValueError("ID do chamado é obrigatório.")

        chamado = self.repository.buscar_por_id(id_chamado)
        if chamado is None:
            raise ValueError("Chamado não encontrado.")
        
        if chamado.data_conclusao is not None:
            raise ValueError("Chamado já está concluído.")

        if chamado.status == "Cancelado":
            raise ValueError("Chamado está Cancelado.")
    
        if chamado.status == "Concluido":
            raise ValueError("Chamado está concluído.")
            
        chamado.data_conclusao = datetime.now()
        chamado.status = "Concluido"

        suite = self.suite_repository.buscar_por_id(chamado.id_suite)
        if suite:
            outros_abertos = [c for c in self.repository.listar_por_suite(chamado.id_suite)
                    if c.status == "Aberto" and c.id_chamado != chamado.id_chamado]
            if not outros_abertos:
                suite.status = "Disponível"
                self.suite_repository.atualizar(suite)

        return self.repository.atualizar(chamado)

    def cancelar_chamado(self,id_chamado:int):

        if id_chamado is None:
            raise ValueError("ID do chamado é obrigatório.")

        chamado = self.repository.buscar_por_id(id_chamado)
        if chamado is None:
            raise ValueError("Chamado não encontrado.")
        
        if chamado.data_conclusao is not None:
            raise ValueError("Chamado já está concluído.")

        # 3. Validações de estado
        if chamado.status == "Cancelado":
            raise ValueError("Este chamado já está cancelado.")
        
        if chamado.status == "Concluido":
            raise ValueError("Não é possível cancelar um chamado que já foi concluído.")

        chamado.status = "Cancelado"
        chamado.data_conclusao= datetime.now()

        suite = self.suite_repository.buscar_por_id(chamado.id_suite)
        if suite:
            outros_abertos = [c for c in self.repository.listar_por_suite(chamado.id_suite)
                  if c.status == "Aberto" and c.id_chamado != chamado.id_chamado]
            if not outros_abertos:
                suite.status = "Disponível"
                self.suite_repository.atualizar(suite)

        return self.repository.atualizar(chamado)

    def listar_pendentes(self,tipo: str | None = None):
        if tipo is None:
            chamados = self.repository.listar_pendentes()
        elif tipo == "Manutenção" or tipo == "Limpeza":
            chamados = self.repository.listar_pendentes(tipo)
        else: raise ValueError("Parametro deve ser None, Manutenção, Limpeza")

        chamados.sort(key=lambda c: (self.ORDEM_PRIORIDADE[c.prioridade], c.data_abertura))
        return chamados
        
    def listar_por_suite(self,id_suite:int):
        # 1. Validação do ID da Suíte
        if id_suite is None:
            raise ValueError("ID da suíte é obrigatório.")
        
        # 2. Validação se a suíte existe no banco
        suite = self.suite_repository.buscar_por_id(id_suite)
        if not suite:
            raise ValueError(f"Suíte #{id_suite} não encontrada.")

        return self.repository.listar_por_suite(id_suite)

    def listar_concluidos(self):
        return self.repository.listar_concluidos()

    def listar_cancelados(self):
        return self.repository.listar_cancelados()


    