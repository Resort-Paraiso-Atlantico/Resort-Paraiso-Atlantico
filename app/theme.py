"""
Tema visual padronizado e moderno do Resort Paraíso Atlântico ("Riviera Luxury").
Proporciona uma experiência visual elegante, refinada e consistente em todas as páginas.
"""

import streamlit as st

# Paleta Riviera Luxury
PRIMARY_DARK = "#0F172A"   # Deep Navy / Slate
PRIMARY_TEAL = "#0D9488"   # Royal Teal Accent
ACCENT_GOLD = "#D97706"    # Warm Luxury Gold
ACCENT_CORAL = "#E11D48"   # Crimson / Coral CTA
BG_LIGHT = "#F8FAFC"       # Soft Warm Background
TEXT_DARK = "#1E293B"      # Dark slate text for maximum legibility
TEXT_MUTED = "#64748B"     # Muted text
CARD_BG = "#FFFFFF"        # Pure white cards

# Badges harmonizados por status
_BADGES = {
    "Disponível": ("#ECFDF5", "#047857"),
    "Confirmada": ("#ECFDF5", "#047857"),
    "Concluído": ("#ECFDF5", "#047857"),
    "Normal": ("#ECFDF5", "#047857"),
    "Ativo": ("#ECFDF5", "#047857"),
    
    "Hospedado": ("#EFF6FF", "#1D4ED8"),
    "Em andamento": ("#EFF6FF", "#1D4ED8"),
    "Pago": ("#EFF6FF", "#1D4ED8"),
    
    "Finalizada": ("#F1F5F9", "#475569"),
    "Encerrado": ("#F1F5F9", "#475569"),
    "Entregue": ("#F1F5F9", "#475569"),
    
    "Ocupada": ("#FEF2F2", "#B91C1C"),
    "Sem estoque": ("#FEF2F2", "#B91C1C"),
    "Crítico": ("#FEF2F2", "#B91C1C"),
    "Cancelada": ("#FEF2F2", "#B91C1C"),
    
    "Pendente": ("#FFFBEB", "#B45309"),
    "Manutenção": ("#FFFBEB", "#B45309"),
    "Estoque baixo": ("#FFFBEB", "#B45309"),
    "🟡 Estoque baixo": ("#FFFBEB", "#B45309"),
    "🔴 Sem estoque": ("#FEF2F2", "#B91C1C"),
    "🟢 Normal": ("#ECFDF5", "#047857"),
}


def aplicar_tema():
    """Injeta o CSS compartilhado e padronizado. Deve ser chamado no topo de cada página."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        /* Container principal */
        [data-testid="stAppViewContainer"] {{
            background-color: {BG_LIGHT};
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: {TEXT_DARK};
        }}

        /* Cabeçalho luxuoso de página */
        .resort-page-header {{
            display: flex;
            align-items: center;
            gap: 1.2rem;
            background: linear-gradient(135deg, {PRIMARY_DARK} 0%, #1E293B 60%, {PRIMARY_TEAL} 100%);
            border-radius: 18px;
            padding: 1.4rem 1.8rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .resort-page-header-icon {{
            font-size: 2.2rem;
            line-height: 1;
            background: rgba(255, 255, 255, 0.12);
            padding: 0.7rem;
            border-radius: 14px;
            backdrop-filter: blur(8px);
        }}
        .resort-page-header-title {{
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            font-size: 1.75rem;
            color: #FFFFFF !important;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .resort-page-header-subtitle {{
            font-weight: 400;
            font-size: 0.92rem;
            color: {ACCENT_GOLD} !important;
            margin: 0.2rem 0 0 0;
        }}

        /* ── Sidebar de navegação ── */
        [data-testid="stSidebar"] {{
            background-color: {PRIMARY_DARK} !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        [data-testid="stSidebar"] * {{
            color: #E2E8F0 !important;
        }}
        [data-testid="stSidebarNav"] a {{
            border-radius: 12px !important;
            margin: 2px 8px !important;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: linear-gradient(135deg, {PRIMARY_TEAL} 0%, #0F766E 100%) !important;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] span {{
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }}

        /* Abas padronizadas */
        button[data-baseweb="tab"] {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: {TEXT_MUTED} !important;
            padding: 0.8rem 1.4rem !important;
            border-radius: 8px 8px 0 0 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PRIMARY_TEAL} !important;
        }}
        [data-baseweb="tab-highlight"] {{
            background-color: {PRIMARY_TEAL} !important;
            height: 3px !important;
        }}

        /* Inputs e formulários */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea {{
            background-color: #FFFFFF !important;
            color: {TEXT_DARK} !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            font-size: 0.92rem !important;
        }}
        [data-testid="stTextInput"] input:focus,
        [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {{
            border-color: {PRIMARY_TEAL} !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
        }}

        /* Labels */
        [data-testid="stWidgetLabel"] p {{
            color: {TEXT_DARK} !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }}

        /* Popover e Dropdown */
        div[data-baseweb="popover"] li {{
            background-color: #FFFFFF !important;
            color: {TEXT_DARK} !important;
        }}

        /* Botões Primários */
        button[kind="primary"], div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(135deg, {ACCENT_CORAL} 0%, #BE123C 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(225, 29, 72, 0.25) !important;
            transition: all 0.2s ease !important;
        }}
        button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {{
            box-shadow: 0 6px 16px rgba(225, 29, 72, 0.35) !important;
            transform: translateY(-1px);
        }}
        button[kind="primary"] p, div[data-testid="stFormSubmitButton"] button p {{
            color: #FFFFFF !important;
        }}

        /* Botões Secundários */
        div[data-testid="stButton"] button {{
            border-radius: 10px !important;
            border: 1px solid #CBD5E1 !important;
            background-color: #FFFFFF !important;
            color: {TEXT_DARK} !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stButton"] button:hover {{
            border-color: {PRIMARY_TEAL} !important;
            color: {PRIMARY_TEAL} !important;
            background-color: #F0FDFA !important;
        }}

        /* Métricas (st.metric) */
        [data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 0.8rem 1rem !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            min-width: 0 !important;
        }}
        [data-testid="stMetricLabel"] p {{
            color: {TEXT_MUTED} !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] * {{
            color: {PRIMARY_DARK} !important;
            font-weight: 700 !important;
            font-size: clamp(1.05rem, 1.6vw, 1.4rem) !important;
            white-space: normal !important;
            word-break: break-word !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }}

        /* Card Padronizado */
        .resort-card {{
            background: {CARD_BG};
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .resort-card:hover {{
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
            border-color: #CBD5E1;
        }}
        .resort-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.6rem;
        }}
        .resort-card-title {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 700;
            font-size: 1.1rem;
            color: {PRIMARY_DARK};
            margin: 0;
        }}
        .resort-card-subtitle {{
            font-size: 0.85rem;
            color: {PRIMARY_TEAL};
            font-weight: 600;
            margin-bottom: 0.4rem;
        }}
        .resort-card-body {{
            font-size: 0.88rem;
            color: {TEXT_MUTED};
            line-height: 1.5;
        }}
        .resort-badge {{
            display: inline-block;
            padding: 0.25rem 0.8rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        /* Subcabeçalhos */
        .stMarkdown h3 {{
            color: {PRIMARY_DARK} !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecalho(titulo: str, subtitulo: str = "", icone: str = "🏨"):
    """Renderiza o cabeçalho padrão de página."""
    sub_html = f'<p class="resort-page-header-subtitle">{subtitulo}</p>' if subtitulo else ""
    html = f'<div class="resort-page-header"><div class="resort-page-header-icon">{icone}</div><div><p class="resort-page-header-title">{titulo}</p>{sub_html}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def badge_status(status: str) -> str:
    """Retorna o HTML de um badge colorido para o status informado."""
    bg, fg = _BADGES.get(status, ("#F1F5F9", "#475569"))
    return f'<span class="resort-badge" style="background:{bg};color:{fg};">{status}</span>'


def card_item(titulo: str, subtitulo: str = "", detalhes_html: str = "", status: str = None) -> str:
    """Retorna HTML de um card visual padronizado para listagens."""
    badge = badge_status(status) if status else ""
    sub = f'<div class="resort-card-subtitle">{subtitulo}</div>' if subtitulo else ""
    detalhes_clean = "".join(line.strip() for line in detalhes_html.splitlines()) if detalhes_html else ""
    return f'<div class="resort-card"><div class="resort-card-header"><span class="resort-card-title">{titulo}</span>{badge}</div>{sub}<div class="resort-card-body">{detalhes_clean}</div></div>'