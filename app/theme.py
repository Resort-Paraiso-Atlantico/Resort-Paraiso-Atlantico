"""
Tema visual compartilhado do Resort Paraíso Atlântico.
Usado pelas páginas internas (Suítes, Reservas, etc.) para manter
a mesma identidade visual da tela de login.
"""

import streamlit as st

# Paleta oficial do resort
OCEAN_DEEP = "#0B3D3A"
OCEAN_MID = "#12617A"
SAND = "#FBF6EC"
GOLD = "#F2C879"
CORAL = "#E8734A"

# Cores de badge por status (fundo claro, texto escuro da mesma família)
_BADGES = {
    "Disponível": ("#E1F5EE", "#085041"),
    "Confirmada": ("#E1F5EE", "#085041"),
    "Hospedado": ("#E5F0FA", "#0B3D6B"),
    "Finalizada": ("#EFEEE9", "#3A3A36"),
    "Ocupada": ("#FAECE7", "#4A1B0C"),
    "Pendente": ("#FAEEDA", "#623C06"),
    "Manutenção": ("#FAEEDA", "#623C06"),
    "Cancelada": ("#FCEBEB", "#501313"),
}


def aplicar_tema():
    """Injeta o CSS compartilhado. Chamar uma vez no topo de cada página."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@300;400;500;600&display=swap');

        [data-testid="stAppViewContainer"] {{
            background: {SAND};
        }}
        [data-testid="stHeader"] {{ background: transparent; }}

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        /* Cabeçalho de página */
        .resort-page-header {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            background: linear-gradient(135deg, {OCEAN_DEEP} 0%, {OCEAN_MID} 100%);
            border-radius: 16px;
            padding: 1.3rem 1.6rem;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 30px rgba(11, 61, 58, 0.18);
        }}
        .resort-page-header-icon {{ font-size: 2rem; line-height: 1; }}
        .resort-page-header-title {{
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            font-size: 1.7rem;
            color: {SAND};
            margin: 0;
        }}
        .resort-page-header-subtitle {{
            font-weight: 300;
            font-size: 0.92rem;
            color: {GOLD};
            margin: 0.15rem 0 0 0;
        }}

        /* ── Força cores legíveis independente do tema (claro/escuro) do navegador ── */
        [data-testid="stAppViewContainer"] * {{
            color: {OCEAN_DEEP};
        }}
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {{
            color: {OCEAN_DEEP} !important;
        }}
        [data-testid="stWidgetLabel"] p {{
            color: {OCEAN_DEEP} !important;
            font-weight: 500;
        }}

        /* Campos de formulário: fundo branco, texto escuro, sempre */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea {{
            background-color: #FFFFFF !important;
            color: {OCEAN_DEEP} !important;
            border: 1px solid rgba(11, 61, 58, 0.25) !important;
        }}
        [data-testid="stNumberInput"] button {{
            background-color: #FFFFFF !important;
            color: {OCEAN_DEEP} !important;
        }}

        /* Conteúdo do dropdown do selectbox (abre em popover separado) */
        div[data-baseweb="popover"] li {{
            background-color: #FFFFFF !important;
            color: {OCEAN_DEEP} !important;
        }}

        /* Cabeçalho superior (nome do usuário / botão sair), fora do container principal */
        [data-testid="stHeaderActionElements"], .resort-page-header * {{
            color: inherit;
        }}
        .resort-page-header-title, .resort-page-header-title * {{ color: {SAND} !important; }}
        .resort-page-header-subtitle, .resort-page-header-subtitle * {{ color: {GOLD} !important; }}

        /* ── Sidebar de navegação ── */
        [data-testid="stSidebar"] {{
            background: {OCEAN_DEEP} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {SAND} !important;
        }}
        [data-testid="stSidebarNav"] a {{
            border-radius: 10px !important;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(242, 200, 121, 0.18) !important;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] span {{
            color: {GOLD} !important;
            font-weight: 600 !important;
        }}

        /* ── Botões secundários (ex: "Sair") fora do container principal ── */
        div[data-testid="stButton"] button {{
            background: {OCEAN_DEEP} !important;
            color: {SAND} !important;
            border: 1px solid {OCEAN_MID} !important;
            border-radius: 999px !important;
        }}
        div[data-testid="stButton"] button p {{
            color: {SAND} !important;
        }}

        /* Nome do usuário no topo */
        [data-testid="stMarkdownContainer"] p {{
            color: {OCEAN_DEEP};
        }}

        /* Abas */
        button[data-baseweb="tab"] {{
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
        }}
        [data-baseweb="tab-highlight"] {{
            background-color: {CORAL} !important;
        }}

        /* Botões primários (submit) */
        button[kind="primary"], div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(135deg, {CORAL} 0%, #E0552F 100%) !important;
            color: {SAND} !important;
            border: none !important;
            border-radius: 999px !important;
        }}
        button[kind="primary"] p, div[data-testid="stFormSubmitButton"] button p {{
            color: {SAND} !important;
        }}

        /* Cartão de suíte */
        .resort-suite-card {{
            background: white;
            border: 1px solid rgba(11, 61, 58, 0.08);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 4px 14px rgba(11, 61, 58, 0.06);
        }}
        .resort-suite-card *:not(.resort-badge) {{ color: {OCEAN_DEEP} !important; }}
        .resort-suite-number {{
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            font-size: 1.15rem;
            color: {OCEAN_DEEP};
        }}
        .resort-suite-meta {{
            font-size: 0.85rem;
            color: #5F5E5A;
            margin-top: 0.15rem;
        }}
        .resort-badge {{
            display: inline-block;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 500;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecalho(titulo: str, subtitulo: str = "", icone: str = "🏨"):
    """Renderiza o cabeçalho padrão de página (banner escuro com título serifado)."""
    st.markdown(
        f"""
        <div class="resort-page-header">
            <div class="resort-page-header-icon">{icone}</div>
            <div>
                <p class="resort-page-header-title">{titulo}</p>
                {f'<p class="resort-page-header-subtitle">{subtitulo}</p>' if subtitulo else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_status(status: str) -> str:
    """Retorna o HTML de um badge colorido para o status informado."""
    bg, fg = _BADGES.get(status, ("#F1EFE8", "#2C2C2A"))
    return f'<span class="resort-badge" style="background:{bg};color:{fg};">{status}</span>'