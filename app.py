import zipfile
from io import BytesIO
from datetime import datetime

import streamlit as st
import pandas as pd

from extractor import extrair_dados_nfe, COLUNAS

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Extração de NF-e",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilo — identidade visual "livro-razão fiscal"
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
    --ink: #16302B;
    --ink-soft: #3F5750;
    --paper: #F6F5F1;
    --paper-card: #FFFFFF;
    --line: #D8D4C8;
    --brass: #8B6400;
    --brass-soft: #F1E4C3;
    --ok: #3F6B4E;
    --err: #A0442C;
}

/* Base — fundo e cor de texto padrão */
.stApp, .stApp > * {
    background-color: #F6F5F1 !important;
    color: #16302B !important;
}

html, body {
    font-family: 'Inter', sans-serif !important;
    color: #16302B !important;
    background-color: #F6F5F1 !important;
}

/* Textos gerais do Streamlit */
p, span, div, label, li, td, th, caption,
.stMarkdown, .stMarkdown p, .stMarkdown span,
.stText, .stCaption,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stText"],
[data-testid="stCaption"] {
    color: #16302B !important;
    font-family: 'Inter', sans-serif !important;
}

/* Ícones do Streamlit (seta da sidebar, seta do expander etc.) usam a fonte
   "Material Symbols" para converter o nome do ícone em glifo — a regra acima
   sobrescrevia essa fonte e fazia aparecer o texto bruto (ex: "keyboard_double_arrow_right") */
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}

/* Títulos */
h1, h2, h3, h4, h5, h6,
.stHeading, [data-testid="stHeading"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #16302B !important;
    letter-spacing: -0.01em !important;
}

/* Sidebar */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #EFEDE4 !important;
    border-right: 1px solid #D8D4C8 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #16302B !important;
}

/* Inputs da sidebar */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    color: #16302B !important;
    background-color: #FFFFFF !important;
    border-color: #D8D4C8 !important;
}

/* Labels de inputs */
.stTextInput label, .stMultiSelect label,
.stSelectbox label, .stFileUploader label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #16302B !important;
    font-weight: 500 !important;
}

/* Campos de texto e multiselect */
.stTextInput input,
.stMultiSelect [data-baseweb="select"] span,
.stMultiSelect [data-baseweb="tag"] span {
    color: #16302B !important;
    background-color: #FFFFFF !important;
}

/* Multiselect — tags e placeholder */
[data-baseweb="select"] [data-baseweb="tag"] {
    background-color: #D8D4C8 !important;
    color: #16302B !important;
}
[data-baseweb="select"] input::placeholder {
    color: #3F5750 !important;
}

/* Expander */
.streamlit-expanderHeader, .streamlit-expanderHeader p,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #16302B !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] {
    border: 1px solid #D8D4C8 !important;
    border-radius: 4px !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background-color: #FFFFFF !important;
    border: 1.5px dashed #D8D4C8 !important;
    color: #16302B !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
    color: #3F5750 !important;
}

/* Streamlit não tem i18n nativo — textos do uploader vêm em inglês fixo,
   então trocamos por conteúdo em PT-BR via ::after (mesma estrutura na v1.50) */
[data-testid="stFileUploaderDropzoneInstructions"] div span:first-child {
    font-size: 0;
}
[data-testid="stFileUploaderDropzoneInstructions"] div span:first-child::after {
    content: "Arraste e solte os arquivos aqui";
    font-size: 1rem;
}
[data-testid="stFileUploaderDropzoneInstructions"] div span:last-child {
    font-size: 0;
}
[data-testid="stFileUploaderDropzoneInstructions"] div span:last-child::after {
    content: "Limite de 200MB por arquivo • XML, ZIP";
    font-size: 0.875rem;
}
[data-testid="stFileUploaderDropzone"] button {
    font-size: 0;
}
[data-testid="stFileUploaderDropzone"] button::after {
    content: "Procurar arquivos";
    font-size: 0.875rem;
    font-family: 'Inter', sans-serif;
}

/* Progresso */
[data-testid="stStatusLabel"], .stProgress p {
    color: #16302B !important;
}

/* Dataframe / tabela */
[data-testid="stDataFrame"] {
    border: 1px solid #D8D4C8 !important;
    border-radius: 4px !important;
}

/* Alertas / info */
.stAlert, [data-testid="stAlert"] {
    border-radius: 4px !important;
}
.stAlert p, [data-testid="stAlert"] p {
    color: #16302B !important;
}

/* Botões */
.stButton > button, .stDownloadButton > button {
    background-color: #16302B !important;
    color: #F6F5F1 !important;
    border-radius: 3px !important;
    border: 1px solid #16302B !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background-color: #3F5750 !important;
    border-color: #3F5750 !important;
    color: #F6F5F1 !important;
}
/* O rótulo do botão fica dentro de [data-testid="stMarkdownContainer"], que a
   regra de "Textos gerais" força para #16302B — sem isso o texto some no fundo escuro do botão */
.stButton [data-testid="stMarkdownContainer"] p,
.stButton [data-testid="stMarkdownContainer"] span,
.stDownloadButton [data-testid="stMarkdownContainer"] p,
.stDownloadButton [data-testid="stMarkdownContainer"] span {
    color: #F6F5F1 !important;
}

/* Cabeçalho / protocolo */
.ledger-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 2px solid #16302B;
    padding-bottom: 14px;
    margin-bottom: 6px;
}
.ledger-header .title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: #16302B;
    line-height: 1.1;
}
.ledger-header .subtitle {
    font-size: 0.95rem;
    color: #3F5750;
    margin-top: 4px;
}
.ledger-header .protocolo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #8B6400;
    background: #F1E4C3;
    border: 1px solid #8B6400;
    padding: 5px 10px;
    border-radius: 3px;
    white-space: nowrap;
}

/* Cards de métrica */
.metric-row { display: flex; gap: 14px; margin: 18px 0 22px 0; flex-wrap: wrap; }
.metric-card {
    flex: 1;
    min-width: 150px;
    background: #FFFFFF;
    border: 1px solid #D8D4C8;
    border-left: 4px solid #16302B;
    border-radius: 4px;
    padding: 14px 16px;
}
.metric-card.brass { border-left-color: #8B6400; }
.metric-card.err   { border-left-color: #A0442C; }
.metric-card .label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #3F5750;
}
.metric-card .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 600;
    color: #16302B;
    margin-top: 2px;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def coletar_arquivos_xml(arquivos_upload):
    """Recebe a lista de uploads (xml e/ou zip) e devolve pares (nome, fonte)."""
    fontes = []
    for arq in arquivos_upload:
        if arq.name.lower().endswith('.zip'):
            with zipfile.ZipFile(arq) as z:
                for info in z.infolist():
                    if info.filename.lower().endswith('.xml') and not info.is_dir():
                        conteudo = z.read(info.filename)
                        fontes.append((info.filename.split('/')[-1], BytesIO(conteudo)))
        else:
            fontes.append((arq.name, arq))
    return fontes


def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    output.seek(0)
    return output


def metric_card(label, value, variant=""):
    return f"""<div class="metric-card {variant}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>"""


# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------

protocolo = datetime.now().strftime("LOTE-%Y%m%d-%H%M")

st.markdown(f"""
<div class="ledger-header">
    <div>
        <div class="title">Extração de NF-e</div>
        <div class="subtitle">Destinatário, UF e produtos extraídos direto do XML</div>
    </div>
    <div class="protocolo">{protocolo}</div>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ Como usar"):
    st.markdown("""
    1. Envie arquivos **.xml** e/ou **.zip** (o zip pode conter vários XMLs, inclusive em subpastas).
    2. Clique em **Processar**.
    3. Filtre por Estado ou Produto na barra lateral, se quiser.
    4. Baixe o Excel com o resultado.

    **Campos extraídos** (da tag `<dest>` e de cada item `<det><prod>`):
    Nome, CPF, CNPJ, UF (`enderDest`), Código do Produto (`cProd`), Descrição do Produto (`xProd`).

    Cada produto de uma NF-e vira **uma linha**, repetindo os dados do destinatário —
    assim fica fácil filtrar por Estado e por Produto na planilha.
    """)

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

arquivos_upload = st.file_uploader(
    "Selecione arquivos XML ou um ZIP com vários XMLs",
    type=['xml', 'zip'],
    accept_multiple_files=True,
)

if arquivos_upload:
    fontes = coletar_arquivos_xml(arquivos_upload)
    st.caption(f"{len(fontes)} arquivo(s) XML pronto(s) para processar.")

    if st.button("▶️ Processar", type="primary"):
        linhas = []
        progress = st.progress(0)
        status = st.empty()
        total = len(fontes)

        for idx, (nome, fonte) in enumerate(fontes):
            status.text(f"Processando: {nome}")
            linhas.extend(extrair_dados_nfe(fonte, nome))
            progress.progress((idx + 1) / total)

        status.empty()
        progress.empty()

        df = pd.DataFrame(linhas, columns=COLUNAS)
        st.session_state['df'] = df
        st.session_state['excel'] = converter_para_excel(df)

# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

if 'df' in st.session_state:
    df = st.session_state['df']

    # --- filtros na sidebar ---
    with st.sidebar:
        st.markdown("### Filtros")
        estados = sorted([u for u in df['UF'].dropna().unique() if u])
        uf_sel = st.multiselect("Estado (UF)", estados)
        produto_busca = st.text_input("Buscar produto (código ou descrição)")
        nome_busca = st.text_input("Buscar destinatário (nome)")

    df_filtrado = df.copy()
    if uf_sel:
        df_filtrado = df_filtrado[df_filtrado['UF'].isin(uf_sel)]
    if produto_busca:
        termo = produto_busca.lower()
        df_filtrado = df_filtrado[
            df_filtrado['Codigo_Produto'].str.lower().str.contains(termo, na=False)
            | df_filtrado['Descricao_Produto'].str.lower().str.contains(termo, na=False)
        ]
    if nome_busca:
        termo = nome_busca.lower()
        df_filtrado = df_filtrado[df_filtrado['Nome'].str.lower().str.contains(termo, na=False)]

    arquivos_com_erro = df[df['Nome'].astype(str).str.startswith('Erro:')]['Arquivo'].nunique()

    st.markdown(f"""
    <div class="metric-row">
        {metric_card("Arquivos processados", df['Arquivo'].nunique())}
        {metric_card("Linhas (produtos)", len(df))}
        {metric_card("Estados distintos", df['UF'].nunique(), "brass")}
        {metric_card("Arquivos com erro", arquivos_com_erro, "err" if arquivos_com_erro else "")}
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 Resultado" + (f" — filtrado ({len(df_filtrado)} de {len(df)} linhas)" if len(df_filtrado) != len(df) else ""))
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    excel_filtrado = converter_para_excel(df_filtrado)
    st.download_button(
        label="⬇️ Baixar resultado filtrado (Excel)",
        data=excel_filtrado,
        file_name="resultado_extracao_nfe.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
else:
    st.info("👆 Envie arquivos XML ou um ZIP para começar.")
