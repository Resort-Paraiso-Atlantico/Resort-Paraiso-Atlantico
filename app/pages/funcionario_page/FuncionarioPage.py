import re
import streamlit as st
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.services.funcionario_service.FuncionarioService import FuncionarioService
from app.theme import aplicar_tema, cabecalho, card_item
from app.utils.search_utils import atende_termo_busca, sanitizar_documento

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Funcionários", "Cadastre e gerencie a equipe de colaboradores do resort", "👨‍💼")


def _formatar_cpf(cpf: str) -> str:
    cpf_limpo = sanitizar_documento(cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    elif len(cpf_limpo) == 9:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:]}"
    return cpf or "—"


def _email_valido(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def obter_cargos_disponiveis(funcionarios):
    padrao = [
        "Recepcionista",
        "Gerente",
        "Camareiro(a)",
        "Chef de Cozinha",
        "Garçom/Garçonete",
        "Atendente",
        "Manutenção",
        "Segurança",
        "Governança",
        "Recreador(a)"
    ]
    existentes = [f.cargo for f in funcionarios if f.cargo]
    return sorted(list(set(padrao + existentes)))


@st.dialog("➕ Cadastrar Novo Funcionário")
def modal_cadastrar_funcionario(service, funcionarios):
    cpf = st.text_input("CPF", placeholder="Somente números ou 000.000.000-00", max_chars=14, key="cad_func_cpf")
    nome = st.text_input("Nome Completo", key="cad_func_nome")
    telefone = st.text_input("Telefone", placeholder="(00) 00000-0000", key="cad_func_tel")
    email = st.text_input("E-mail", key="cad_func_email")

    opcoes_cargos = obter_cargos_disponiveis(funcionarios) + ["➕ Outro (Novo Cargo...)"]
    cargo_sel = st.selectbox("Cargo", opcoes_cargos, key="cad_func_cargo_sel")
    if cargo_sel == "➕ Outro (Novo Cargo...)":
        cargo = st.text_input("Digite o Nome do Novo Cargo", placeholder="Ex: Supervisor de TI", key="cad_func_cargo_custom")
    else:
        cargo = cargo_sel

    salario = st.number_input("Salário (R$)", min_value=0.01, value=2500.00, step=100.0, format="%.2f", key="cad_func_salario")

    if st.button("Cadastrar Funcionário", type="primary", width="stretch", key="btn_cad_func_submit"):
        cpf_limpo = sanitizar_documento(cpf)
        if not cpf_limpo:
            st.error("CPF é obrigatório.")
        elif not nome.strip():
            st.error("Nome é obrigatório.")
        elif not telefone.strip():
            st.error("Telefone é obrigatório.")
        elif not _email_valido(email):
            st.error("Informe um e-mail válido.")
        elif not cargo or not cargo.strip():
            st.error("Cargo é obrigatório.")
        elif salario <= 0:
            st.error("Salário deve ser maior que zero.")
        else:
            try:
                service.criar_funcionario(
                    cpf_funcionario=cpf_limpo,
                    nome=nome.strip(),
                    telefone=telefone.strip(),
                    email=email.strip(),
                    cargo=cargo.strip().title(),
                    salario=salario
                )
                st.success("Funcionário cadastrado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except IntegrityError:
                st.error("Já existe um funcionário cadastrado com este CPF.")
            except Exception as e:
                st.error(f"Erro ao cadastrar funcionário: {str(e)}")


@st.dialog("✏️ Editar Funcionário")
def modal_editar_funcionario(service, funcionario, funcionarios):
    st.caption(f"Editando dados do funcionário **CPF: {_formatar_cpf(funcionario.cpf_funcionario)}**")
    nome = st.text_input("Nome Completo", value=funcionario.nome, key=f"edit_func_nome_{funcionario.cpf_funcionario}")
    telefone = st.text_input("Telefone", value=funcionario.telefone or "", key=f"edit_func_tel_{funcionario.cpf_funcionario}")
    email = st.text_input("E-mail", value=funcionario.email or "", key=f"edit_func_email_{funcionario.cpf_funcionario}")

    opcoes_cargos = obter_cargos_disponiveis(funcionarios) + ["➕ Outro (Novo Cargo...)"]
    idx_cargo = opcoes_cargos.index(funcionario.cargo) if funcionario.cargo in opcoes_cargos[:-1] else len(opcoes_cargos) - 1
    cargo_sel = st.selectbox("Cargo", opcoes_cargos, index=idx_cargo, key=f"edit_func_cargo_sel_{funcionario.cpf_funcionario}")

    if cargo_sel == "➕ Outro (Novo Cargo...)":
        default_custom = funcionario.cargo if funcionario.cargo not in opcoes_cargos[:-1] else ""
        cargo = st.text_input("Digite o Nome do Novo Cargo", value=default_custom, key=f"edit_func_cargo_custom_{funcionario.cpf_funcionario}")
    else:
        cargo = cargo_sel

    salario = st.number_input(
        "Salário (R$)",
        min_value=0.01,
        value=float(funcionario.salario),
        step=100.0,
        format="%.2f",
        key=f"edit_func_salario_{funcionario.cpf_funcionario}"
    )

    if st.button("Salvar Alterações", type="primary", width="stretch", key=f"btn_edit_func_submit_{funcionario.cpf_funcionario}"):
        if not nome.strip():
            st.error("Nome é obrigatório.")
        elif not telefone.strip():
            st.error("Telefone é obrigatório.")
        elif not _email_valido(email):
            st.error("Informe um e-mail válido.")
        elif not cargo or not cargo.strip():
            st.error("Cargo é obrigatório.")
        elif salario <= 0:
            st.error("Salário deve ser maior que zero.")
        else:
            try:
                service.atualizar_funcionario(
                    cpf_funcionario=funcionario.cpf_funcionario,
                    nome=nome.strip(),
                    telefone=telefone.strip(),
                    email=email.strip(),
                    cargo=cargo.strip().title(),
                    salario=salario
                )
                st.success("Funcionário atualizado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao atualizar funcionário: {str(e)}")



with SessionLocal() as db:
    service = FuncionarioService(db)
    funcionarios = service.listar_funcionarios()

    col_busca, col_cargo, col_vis, col_btn = st.columns([3, 2, 2, 2])
    with col_busca:
        termo_busca = st.text_input(
            "🔍 Pesquisar funcionário",
            placeholder="Nome, CPF, cargo, e-mail ou telefone...",
            key="busca_funcionarios"
        )
    with col_cargo:
        cargos = ["Todos"] + obter_cargos_disponiveis(funcionarios)
        cargo_filtro = st.selectbox("Cargo", cargos, key="filtro_cargo_func")
    with col_vis:
        modo_vis = st.radio(
            "Modo de Visão",
            ["🎴 Cards", "📊 Tabela"],
            horizontal=True,
            label_visibility="collapsed",
            key="vis_funcionarios"
        )
    with col_btn:
        if st.button("➕ Novo Funcionário", type="primary", width="stretch", key="btn_novo_func_top"):
            modal_cadastrar_funcionario(service, funcionarios)

    funcionarios_filtrados = [
        f for f in funcionarios
        if atende_termo_busca(termo_busca, f.nome, f.cpf_funcionario, f.email, f.telefone, f.cargo)
        and (cargo_filtro == "Todos" or f.cargo == cargo_filtro)
    ]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Funcionários", len(funcionarios_filtrados))
    folha_total = sum(f.salario for f in funcionarios_filtrados)
    c2.metric("Folha Salarial Total", f"R$ {folha_total:,.2f}")
    media_salaria = (folha_total / len(funcionarios_filtrados)) if funcionarios_filtrados else 0.0
    c3.metric("Média Salarial", f"R$ {media_salaria:,.2f}")
    cargos_distintos = len(set(f.cargo for f in funcionarios_filtrados))
    c4.metric("Cargos Distintos", cargos_distintos)

    st.divider()

    if not funcionarios_filtrados:
        if termo_busca or cargo_filtro != "Todos":
            st.info("Nenhum funcionário encontrado com os filtros aplicados.")
        else:
            st.info("Nenhum funcionário cadastrado ainda.")
    else:
        if modo_vis == "📊 Tabela":
            dados_tabela = [
                {
                    "CPF": _formatar_cpf(f.cpf_funcionario),
                    "Nome Completo": f.nome,
                    "Cargo": f.cargo,
                    "Telefone": f.telefone or "—",
                    "E-mail": f.email or "—",
                    "Salário": float(f.salario)
                }
                for f in funcionarios_filtrados
            ]
            st.dataframe(
                dados_tabela,
                width="stretch",
                column_config={
                    "CPF": st.column_config.TextColumn("CPF", width="small"),
                    "Nome Completo": st.column_config.TextColumn("Funcionário", width="medium"),
                    "Cargo": st.column_config.TextColumn("Cargo", width="medium"),
                    "Telefone": st.column_config.TextColumn("Telefone", width="small"),
                    "E-mail": st.column_config.TextColumn("E-mail", width="medium"),
                    "Salário": st.column_config.NumberColumn("Salário", format="R$ %.2f"),
                }
            )

            st.caption("⚙️ **Ações Rápidas da Tabela:**")
            c_act1, c_act2, c_act3 = st.columns([4, 2, 2])
            with c_act1:
                func_sel_tab = st.selectbox(
                    "Selecione um funcionário da tabela para alterar",
                    funcionarios_filtrados,
                    format_func=lambda f: f"{f.nome} - {f.cargo} (CPF: {_formatar_cpf(f.cpf_funcionario)})",
                    key="sel_tab_func",
                    index=None,
                    placeholder="Selecione um funcionário..."
                )
            with c_act2:
                if st.button("✏️ Editar Funcionário", key="btn_edit_tab_func", width="stretch", disabled=not func_sel_tab):
                    modal_editar_funcionario(service, func_sel_tab, funcionarios)
            with c_act3:
                if st.button("🗑️ Excluir Funcionário", key="btn_del_tab_func", width="stretch", disabled=not func_sel_tab):
                    try:
                        service.remover_funcionario(func_sel_tab.cpf_funcionario)
                        st.success(f"Funcionário {func_sel_tab.nome} removido.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro ao remover funcionário: {str(e)}")
        else:
            cols = st.columns(2)
            for i, f in enumerate(funcionarios_filtrados):
                detalhes = f"""
                <strong>CPF:</strong> {_formatar_cpf(f.cpf_funcionario)}<br>
                💼 <strong>Cargo:</strong> {f.cargo}<br>
                📞 {f.telefone or '—'} &nbsp;·&nbsp; ✉️ {f.email or '—'}<br>
                💵 <strong>Salário:</strong> R$ {f.salario:,.2f}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(
                            f.nome,
                            f"Cargo: {f.cargo}",
                            detalhes,
                            status="Ativo"
                        ),
                        unsafe_allow_html=True,
                    )
                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        if st.button("✏️ Editar", key=f"btn_edit_func_{f.cpf_funcionario}", width="stretch"):
                            modal_editar_funcionario(service, f, funcionarios)
                    with c_del:
                        if st.button("🗑️ Excluir", key=f"btn_del_func_{f.cpf_funcionario}", width="stretch"):
                            try:
                                service.remover_funcionario(f.cpf_funcionario)
                                st.success(f"Funcionário {f.nome} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                            except Exception as e:
                                st.error(f"Erro ao remover funcionário: {str(e)}")
