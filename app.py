"""Dashboard Sueño Dorado - Control de Pagos | Nivel Ejecutivo"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(
    page_title="Sueño Dorado | Control de Pagos",
    layout="wide",
    page_icon="💰",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0f1c;
        --bg-secondary: #111827;
        --bg-card: #1a1f2e;
        --bg-card-hover: #232b3e;
        --border: rgba(255,255,255,0.06);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-blue: #3b82f6;
        --accent-blue-dim: rgba(59,130,246,0.15);
        --accent-emerald: #10b981;
        --accent-emerald-dim: rgba(16,185,129,0.15);
        --accent-amber: #f59e0b;
        --accent-amber-dim: rgba(245,158,11,0.15);
        --accent-rose: #f43f5e;
        --accent-rose-dim: rgba(244,63,94,0.15);
        --shadow: 0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -2px rgba(0,0,0,0.2);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -4px rgba(0,0,0,0.3);
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: var(--bg-primary); }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--bg-card); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
    
    /* Header Premium */
    .header-container {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        background: linear-gradient(135deg, var(--accent-blue-dim) 0%, transparent 60%);
        pointer-events: none;
    }
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    .header-date {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 12px 12px 0 0;
    }
    .metric-card.blue::before { background: var(--accent-blue); }
    .metric-card.emerald::before { background: var(--accent-emerald); }
    .metric-card.amber::before { background: var(--accent-amber); }
    .metric-card.rose::before { background: var(--accent-rose); }
    
    .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    .section-line {
        flex: 1;
        height: 1px;
        background: var(--border);
    }
    
    /* Chart Container */
    .chart-container {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge.blue { background: var(--accent-blue-dim); color: var(--accent-blue); }
    .badge.emerald { background: var(--accent-emerald-dim); color: var(--accent-emerald); }
    .badge.amber { background: var(--accent-amber-dim); color: var(--accent-amber); }
    .badge.rose { background: var(--accent-rose-dim); color: var(--accent-rose); }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background: var(--bg-secondary) !important; 
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card);
        color: var(--text-primary);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--accent-blue) !important;
        color: white !important;
        border-color: var(--accent-blue);
    }
    
    /* DataFrame */
    .dataframe {
        border: none !important;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border);
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label {
        color: var(--text-secondary) !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--accent-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #2563eb;
        box-shadow: var(--shadow);
    }
    
    /* Number Input */
    [data-testid="stNumberInput"] input {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-primary);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: var(--accent-blue);
    }
</style>
""",
    unsafe_allow_html=True,
)


def generar_pdf_profesional(df_f, tipo_cambio, totales, filtros_info):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Colores minimalistas
    PRIMARY = "#0a1628"
    ACCENT = "#3b82f6"
    SUCCESS = "#10b981"
    GRAY = "#64748b"
    WARNING = "#f59e0b"

    # Header minimalista con filtros
    periodo = filtros_info.get("periodo", "Todo")
    bancos = filtros_info.get("bancos", "Todos")

    header_data = [
        ["SUEÑO DORADO", f"Periodo: {periodo}", datetime.now().strftime("%d %b %Y")],
        ["Cuentas por Cobrar - ISD", f"Bancos: {bancos}", f"TC: S/. {tipo_cambio:.2f}"],
    ]
    header_table = Table(header_data, colWidths=[200, 350, 100])
    header_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (0, 0), 16),
                ("FONTSIZE", (0, 1), (0, 1), 10),
                ("FONTSIZE", (1, 0), (1, -1), 9),
                ("FONTSIZE", (2, 0), (2, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), rl_colors.HexColor(PRIMARY)),
                ("TEXTCOLOR", (1, 0), (1, -1), rl_colors.HexColor(GRAY)),
                ("TEXTCOLOR", (2, 0), (2, -1), rl_colors.HexColor(GRAY)),
                ("LINEBELOW", (0, 1), (-1, 1), 2, rl_colors.HexColor(ACCENT)),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(header_table)
    elements.append(Spacer(1, 25))

    # Métricas en cards minimalistas
    col_w = 130

    # Calcular porcentaje de mora
    pct_mora = totales["pct_venc"]

    metrics_data = [
        [
            f"{totales['total_docs']}\nDocs",
            f"$ {totales['total_usd']:,.0f}\nCartera USD",
            f"{totales['vencidos']}\nVencidos",
            f"{totales['riesgo_alto']}\nAlto Riesgo",
            f"{pct_mora:.0f}%\nMora",
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[col_w] * 5)
    metrics_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), rl_colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, rl_colors.HexColor("#e2e8f0")),
                ("LINEAFTER", (0, 0), (3, 0), 1, rl_colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    elements.append(metrics_table)
    elements.append(Spacer(1, 25))

    # Por Banco
    por_banco = (
        df_f.groupby("BANCO")
        .agg({"IMPORTE": "sum", "NUMERO UNICO": "count"})
        .reset_index()
        .sort_values("IMPORTE", ascending=False)
    )
    banco_header = [["BANCO", "DOCS", "MONTO"]]
    for _, row in por_banco.iterrows():
        banco_header.append(
            [
                str(row["BANCO"])[:20],
                str(row["NUMERO UNICO"]),
                f"S/. {row['IMPORTE']:,.0f}",
            ]
        )
    banco_table = Table(banco_header, colWidths=[120, 50, 100])
    banco_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(PRIMARY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [rl_colors.white, rl_colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )
    elements.append(banco_table)
    elements.append(Spacer(1, 15))

    # Por Girador
    por_girador = (
        df_f.groupby("GIRADOR")
        .agg({"IMPORTE": "sum", "DIAS VENCIDOS": "max"})
        .reset_index()
        .sort_values("IMPORTE", ascending=False)
        .head(8)
    )
    girador_header = [["GIRADOR", "MONTO", "DIAS"]]
    for _, row in por_girador.iterrows():
        dias = int(row["DIAS VENCIDOS"]) if pd.notna(row["DIAS VENCIDOS"]) else 0
        girador_header.append(
            [str(row["GIRADOR"])[:25], f"S/. {row['IMPORTE']:,.0f}", f"{dias}d"]
        )
    girador_table = Table(girador_header, colWidths=[160, 100, 60])
    girador_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(SUCCESS)),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [rl_colors.white, rl_colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )
    elements.append(girador_table)
    elements.append(Spacer(1, 20))

    # Por Antigüedad
    por_antiguedad = (
        df_f.groupby("RANGO_DIAS")
        .agg({"IMPORTE": "sum", "NUMERO UNICO": "count"})
        .reset_index()
    )
    anti_data = [["RANGO", "DOCS", "MONTO"]]
    for _, row in por_antiguedad.sort_values("RANGO_DIAS").iterrows():
        anti_data.append(
            [
                str(row["RANGO_DIAS"]),
                str(row["NUMERO UNICO"]),
                f"S/. {row['IMPORTE']:,.0f}",
            ]
        )
    anti_table = Table(anti_data, colWidths=[150, 60, 100])
    anti_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(ACCENT)),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [rl_colors.white, rl_colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )
    elements.append(anti_table)
    elements.append(Spacer(1, 30))

    # Detalle de Documentos (Nueva Sección)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("DETALLE DE DOCUMENTOS EXPORTADOS", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    # Seleccionar columnas clave para el detalle
    cols_detalle = ["NUMERO UNICO", "GIRADOR", "BANCO", "Fecha de Vencimiento", "DIAS VENCIDOS", "MONEDA", "IMPORTE"]
    
    # Header del detalle
    detalle_header = [["ID", "GIRADOR", "BANCO", "VENCIMIENTO", "DIAS", "MON", "IMPORTE"]]
    
    # Limitar a los primeros 100 para no hacer el PDF infinito, o dejar que fluya
    for _, row in df_f.head(200).iterrows(): # Limitamos a 200 por rendimiento en PDF
        fecha_v = row["Fecha de Vencimiento"].strftime("%d/%m/%Y") if pd.notna(row["Fecha de Vencimiento"]) else "-"
        dias = int(row["DIAS VENCIDOS"]) if pd.notna(row["DIAS VENCIDOS"]) else 0
        detalle_header.append([
            str(row["NUMERO UNICO"])[:10],
            str(row["GIRADOR"])[:15],
            str(row["BANCO"])[:10],
            fecha_v,
            f"{dias}d",
            str(row["MONEDA"])[:3],
            f"{row['IMPORTE']:,.2f}"
        ])

    detalle_table = Table(detalle_header, colWidths=[60, 110, 80, 80, 40, 40, 80])
    detalle_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(PRIMARY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#e2e8f0")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [rl_colors.white, rl_colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )
    elements.append(detalle_table)
    if len(df_f) > 200:
        elements.append(Paragraph(f"... y {len(df_f)-200} documentos mas (solo se muestran los primeros 200 en el PDF)", styles["Italic"]))

    elements.append(Spacer(1, 30))

    # Footer minimalista
    footer_data = [
        [
            "Sueño Dorado ISD | Reporte Certificado",
            f"Filtros: {filtros_info.get('bancos')} | {filtros_info.get('monedas')}",
            f"Página 1", # Simplificado por ahora
        ]
    ]
    footer_table = Table(footer_data, colWidths=[200, 300, 100])
    footer_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.HexColor(GRAY)),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, rl_colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
            ]
        )
    )
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


@st.cache_data
def cargar_datos():
    import os

    excel_path = os.environ.get(
        "DATA_PATH", "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx"
    )
    df = pd.read_excel(excel_path, sheet_name="DATA ORIGINAL", header=2)

    df = df[df["CONDICION DEUDA"] == "PENDIENTE DE PAGO"]
    df = df[df["IMPORTE"].notna()]

    if "NUMERO UNICO" in df.columns:
        mask = df["NUMERO UNICO"].isna()
        nuevo_numero = df.loc[mask, "Nº LETRA - FACT"].fillna("")
        vacios = nuevo_numero == ""
        nuevo_numero.loc[vacios] = "S/N-" + df.loc[mask][vacios].index.astype(str)
        df.loc[mask, "NUMERO UNICO"] = nuevo_numero

    df["Fecha de Vencimiento"] = pd.to_datetime(
        df["Fecha de Vencimiento"], errors="coerce"
    )
    df["IMPORTE"] = pd.to_numeric(
        df["IMPORTE"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DOLARES"] = pd.to_numeric(
        df["DOLARES"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DIAS VENCIDOS"] = pd.to_numeric(
        df["DIAS VENCIDOS"].astype(str).str.replace(",", ""), errors="coerce"
    )

    df["MES"] = df["Fecha de Vencimiento"].dt.to_period("M").astype(str)
    df["SEMANA"] = df["Fecha de Vencimiento"].dt.isocalendar().week.astype(str)
    df["DIA"] = df["Fecha de Vencimiento"].dt.date
    df["TRIMESTRE"] = df["Fecha de Vencimiento"].dt.to_period("Q").astype(str)

    df["RANGO_DIAS"] = pd.cut(
        df["DIAS VENCIDOS"],
        bins=[-1, 0, 30, 60, 90, 180, 365],
        labels=["Al dia", "1-30", "31-60", "61-90", "91-180", "181-365"],
    )

    return df


def crear_grafico_donut(df, valores, titulo, colores):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=valores.index,
                values=valores.values,
                hole=0.65,
                marker_colors=colores,
                textinfo="percent",
                textposition="outside",
                textfont=dict(color="#94a3b8", size=11),
                hovertemplate="<b>%{label}</b><br>S/. %{value:,.0f}<br>(%{percent})<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(color="#f8fafc", size=14, family="Inter"),
            x=0.5,
            y=0.95,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#94a3b8", size=10),
        ),
        margin=dict(t=30, b=10, l=20, r=20),
        height=280,
    )
    return fig


def crear_grafico_barras(df, x, y, titulo, color):
    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker_color=color,
                hovertemplate="<b>%{x}</b><br>S/. %{y:,.0f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(color="#f8fafc", size=14, family="Inter"),
            x=0.5,
            y=0.95,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            color="#64748b",
            tickfont=dict(color="#64748b", size=10),
            gridcolor="rgba(255,255,255,0.03)",
            showline=False,
        ),
        yaxis=dict(
            color="#64748b",
            tickfont=dict(color="#64748b", size=10),
            gridcolor="rgba(255,255,255,0.03)",
            showline=False,
        ),
        margin=dict(t=30, b=40, l=50, r=20),
        height=280,
        showlegend=False,
    )
    return fig


df = cargar_datos()

# === HEADER ===
ultima_fecha = df["Fecha de Vencimiento"].max()
ultima_fecha_str = (
    pd.to_datetime(ultima_fecha).strftime("%d %b %Y")
    if pd.notna(ultima_fecha)
    else "N/A"
)

st.markdown(
    f"""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <h1 class="header-title">Sueño Dorado</h1>
            <p class="header-subtitle">Control de Pagos ISD - Cuentas por Cobrar</p>
            <p class="header-date">Actualizado: {datetime.now().strftime("%d %b %Y, %H:%M")} | Ultimo documento: {ultima_fecha_str}</p>
        </div>
        <div style="text-align: right;">
            <span class="badge emerald">● En Proceso</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### Configuracion")

    st.markdown("**Tipo de Cambio USD**")
    tipo_cambio = st.number_input(
        "S/. por $1 USD",
        min_value=3.0,
        max_value=5.0,
        value=3.45,
        step=0.01,
    )

    st.markdown("---")
    st.markdown("### Filtros")

    bancos = sorted(df["BANCO"].dropna().unique())
    filtro_banco = st.multiselect("Banco", options=bancos, default=bancos)

    monedas = sorted(df["MONEDA"].dropna().unique())
    filtro_moneda = st.multiselect("Moneda", options=monedas, default=monedas)

    giradores = sorted(df["GIRADOR"].dropna().unique())
    filtro_girador = st.multiselect("Girador", options=giradores, default=giradores)

    productos = sorted(df["PRODUCTO"].dropna().unique())
    filtro_producto = st.multiselect("Producto", options=productos, default=productos)

    st.markdown("---")
    st.markdown("### 📅 Periodo de Vencimiento")
    
    # UI Mejorada para Periodos
    filtro_periodo = st.selectbox(
        "Filtro Rapido:",
        [
            "Todo",
            "Solo Vencidos",
            "Vence Hoy",
            "Esta Semana",
            "Este Mes",
            "3 Meses",
            "Vencidos +7 dias",
            "Vencidos +30 dias",
            "Vencidos +90 dias",
            "Personalizar Rango",
        ],
        index=0,
        help="Selecciona un intervalo de tiempo predefinido o usa el calendario para mayor precision."
    )

    # Mostrar siempre el calendario si se selecciona "Personalizar Rango" o como opción visible
    if filtro_periodo == "Personalizar Rango":
        st.markdown("**Selecciona Intervalo:**")
        fecha_hoy = datetime.now().date()
        fecha_rango = st.date_input(
            "Rango de Fechas:",
            value=(fecha_hoy - timedelta(days=30), fecha_hoy),
            help="Haz clic para abrir el calendario y seleccionar el inicio y fin."
        )
        
        if isinstance(fecha_rango, tuple) and len(fecha_rango) == 2:
            fecha_inicio, fecha_fin = fecha_rango
        else:
            fecha_inicio = fecha_hoy - timedelta(days=30)
            fecha_fin = fecha_hoy
            st.info("💡 Por favor, selecciona una fecha de inicio y una de fin en el calendario.")
    else:
        st.info(f"Filtro activo: {filtro_periodo}")

    st.markdown("---")

# === APLICAR FILTROS ===
df_f = df.copy()

if filtro_banco:
    df_f = df_f[df_f["BANCO"].isin(filtro_banco)]
if filtro_moneda:
    df_f = df_f[df_f["MONEDA"].isin(filtro_moneda)]
if filtro_girador:
    df_f = df_f[df_f["GIRADOR"].isin(filtro_girador)]
if filtro_producto:
    df_f = df_f[df_f["PRODUCTO"].isin(filtro_producto)]

if filtro_periodo == "Solo Vencidos":
    df_f = df_f[df_f["DIAS VENCIDOS"] > 0]
elif filtro_periodo == "Vence Hoy":
    df_f = df_f[df_f["DIAS VENCIDOS"] == 0]
elif filtro_periodo == "Esta Semana":
    desde = datetime.now()
    hasta = datetime.now() + timedelta(days=7)
    df_f = df_f[
        (df_f["Fecha de Vencimiento"] >= pd.to_datetime(desde))
        & (df_f["Fecha de Vencimiento"] <= pd.to_datetime(hasta))
    ]
elif filtro_periodo == "Este Mes":
    desde = datetime.now()
    hasta = datetime.now() + timedelta(days=30)
    df_f = df_f[
        (df_f["Fecha de Vencimiento"] >= pd.to_datetime(desde))
        & (df_f["Fecha de Vencimiento"] <= pd.to_datetime(hasta))
    ]
elif filtro_periodo == "3 Meses":
    desde = datetime.now()
    hasta = datetime.now() + timedelta(days=90)
    df_f = df_f[
        (df_f["Fecha de Vencimiento"] >= pd.to_datetime(desde))
        & (df_f["Fecha de Vencimiento"] <= pd.to_datetime(hasta))
    ]
elif filtro_periodo == "Vencidos +7 dias":
    df_f = df_f[df_f["DIAS VENCIDOS"] > 7]
elif filtro_periodo == "Vencidos +30 dias":
    df_f = df_f[df_f["DIAS VENCIDOS"] > 30]
elif filtro_periodo == "Vencidos +90 dias":
    df_f = df_f[df_f["DIAS VENCIDOS"] > 90]
elif filtro_periodo == "Personalizar Rango":
    df_f = df_f[
        (df_f["Fecha de Vencimiento"] >= pd.to_datetime(fecha_inicio))
        & (df_f["Fecha de Vencimiento"] <= pd.to_datetime(fecha_fin))
    ]

# === CALCULOS ===
soles = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
dolares = df_f[df_f["MONEDA"] == "DOLARES"]["IMPORTE"].sum()
total_usd = soles / tipo_cambio + dolares

vencidos = len(df_f[df_f["DIAS VENCIDOS"] > 0])
al_dia = len(df_f[df_f["DIAS VENCIDOS"] == 0])
por_vencer = len(df_f[df_f["DIAS VENCIDOS"] < 0])

riesgo_alto = len(df_f[df_f["DIAS VENCIDOS"] > 90])
riesgo_medio = len(df_f[(df_f["DIAS VENCIDOS"] > 30) & (df_f["DIAS VENCIDOS"] <= 90)])
riesgo_bajo = len(df_f[(df_f["DIAS VENCIDOS"] > 0) & (df_f["DIAS VENCIDOS"] <= 30)])

# === METRICAS PRINCIPALES ===
st.markdown("### Resumen de Cartera")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
    <div class="metric-card blue">
        <div class="metric-label">Total Documentos</div>
        <div class="metric-value">{len(df_f):,}</div>
        <div class="metric-subtext">{len(df)} en total</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card emerald">
        <div class="metric-label">Cartera Total (USD)</div>
        <div class="metric-value">$ {total_usd:,.0f}</div>
        <div class="metric-subtext">Equivalente en dolares</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card amber">
        <div class="metric-label">Cartera Soles</div>
        <div class="metric-value">S/. {soles:,.0f}</div>
        <div class="metric-subtext">$ {dolares:,.0f} en dolares</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="metric-card rose">
        <div class="metric-label">Vencidos</div>
        <div class="metric-value">{vencidos}</div>
        <div class="metric-subtext">{vencidos / len(df_f) * 100:.1f}% del total</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    pct_venc = vencidos / len(df_f) * 100 if len(df_f) > 0 else 0
    pct_riesgo = riesgo_alto / vencidos * 100 if vencidos > 0 else 0

st.markdown("")

# === ESTADO DE VENCIMIENTO ===
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
    <div class="metric-card rose">
        <div class="metric-label">Vencidos</div>
        <div class="metric-value">{vencidos}</div>
        <div class="metric-subtext">Documents expired</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card emerald">
        <div class="metric-label">Al Dia</div>
        <div class="metric-value">{al_dia}</div>
        <div class="metric-subtext">Vencen hoy</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card blue">
        <div class="metric-label">Por Vencer</div>
        <div class="metric-value">{por_vencer}</div>
        <div class="metric-subtext">Proximos a vencer</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("")

# === RIESGO ===
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
    <div class="metric-card rose">
        <div class="metric-label">Riesgo Alto</div>
        <div class="metric-value">{riesgo_alto}</div>
        <div class="metric-subtext">{pct_riesgo:.0f}% de vencidos</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card amber">
        <div class="metric-label">Riesgo Medio</div>
        <div class="metric-value">{riesgo_medio}</div>
        <div class="metric-subtext">31-90 dias</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card emerald">
        <div class="metric-label">Riesgo Bajo</div>
        <div class="metric-value">{riesgo_bajo}</div>
        <div class="metric-subtext">1-30 dias</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("")

# === ALERTAS ===
alertas = []
if riesgo_alto > 0:
    alertas.append(
        (
            "ALERTA",
            f"{riesgo_alto} documentos con mas de 90 dias de vencimiento - Evaluar provisiones",
            "rose",
        )
    )
if riesgo_medio > 0:
    alertas.append(
        (
            "PRECAUCION",
            f"{riesgo_medio} documentos entre 31-90 dias - Gestionar cobranza",
            "amber",
        )
    )
if al_dia > 0:
    alertas.append(
        ("URGENTE", f"{al_dia} documentos vencen HOY - Cobrar inmediatamente", "amber")
    )
if dolares > 100000:
    alertas.append(
        (
            "INFO",
            f"Exposicion en dolares: $ {dolares:,.0f} - Monitorear tipo de cambio",
            "blue",
        )
    )

if alertas:
    st.markdown("### Alertas")
    for tipo, mensaje, color in alertas:
        color_map = {"rose": "#ef4444", "amber": "#f59e0b", "blue": "#3b82f6"}
        bg_color = {
            "rose": "rgba(239,68,68,0.1)",
            "amber": "rgba(245,158,11,0.1)",
            "blue": "rgba(59,130,246,0.1)",
        }
        st.markdown(
            f"""
        <div style="background: {bg_color[color]}; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-left: 4px solid {color_map[color]};">
            <span style="color: {color_map[color]}; font-weight: 600; font-size: 0.75rem; text-transform: uppercase;">{tipo}</span>
            <span style="color: var(--text-secondary); font-size: 0.85rem; margin-left: 0.5rem;">{mensaje}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# === EXPORTAR PDF ===
# Información de filtros aplicados
filtros_info = {
    "periodo": filtro_periodo,
    "bancos": ", ".join(filtro_banco) if filtro_banco else "Todos",
    "monedas": ", ".join(filtro_moneda) if filtro_moneda else "Todas",
    "tipo_cambio": tipo_cambio,
}

totales = {
    "total_docs": len(df_f),
    "total_usd": total_usd,
    "soles": soles,
    "dolares": dolares,
    "vencidos": vencidos,
    "pct_venc": pct_venc,
    "al_dia": al_dia,
    "riesgo_alto": riesgo_alto,
    "riesgo_medio": riesgo_medio,
    "por_vencer": por_vencer,
}

# Nombre dinámico del archivo
filtro_nombre = filtro_periodo.replace(" ", "_").replace("+", "mas")
filename = f"Reporte_ISD_{filtro_nombre}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

# === CENTRO DE EXPORTACIÓN (Multi-formato) ===
st.markdown("### 📤 Centro de Exportación Pro")
st.markdown(
    """
    <div style="background: rgba(59,130,246,0.05); border-radius: 8px; padding: 1rem; border: 1px solid var(--border); margin-bottom: 1.5rem;">
        <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">
            <b>Consejo de Experto:</b> Utiliza el <b>PDF</b> para presentaciones ejecutivas, 
            el <b>Excel</b> para auditoría de campo y el <b>CSV</b> para backups masivos.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_pdf, col_xlsx, col_csv = st.columns(3)

# 1. EXPORTACIÓN PDF (Reporte Consolidado)
with col_pdf:
    st.markdown("**Reporte Ejecutivo**")
    st.caption("Gráficos + Resumen + Detalle")
    if st.button("📄 Exportar PDF", use_container_width=True, help="Ideal para GERENCIA. Contiene el análisis visual y el resumen de riesgos."):
        with st.spinner("Generando PDF..."):
            try:
                pdf_buffer = generar_pdf_profesional(df_f, tipo_cambio, totales, filtros_info)
                st.download_button(
                    label="💾 Descargar PDF",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success(f"PDF Certificado generado.")
            except Exception as e:
                st.error(f"Error PDF: {str(e)}")

# 2. EXPORTACIÓN EXCEL (Análisis de Auditoría)
with col_xlsx:
    st.markdown("**Auditoría Excel**")
    st.caption("Matriz de Datos + Fórmulas")
    try:
        buffer_xlsx = BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
            df_f.to_excel(writer, index=False, sheet_name='Data_Filtrada_ISD')
        
        st.download_button(
            label="📊 Exportar Excel",
            data=buffer_xlsx.getvalue(),
            file_name=f"Auditoria_ISD_{filtro_nombre}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Ideal para CONTABILIDAD. Permite realizar conciliaciones y tablas dinámicas."
        )
    except Exception as e:
        st.error(f"Error Excel: {str(e)}")

# 3. EXPORTACIÓN CSV (Respaldo Crudo)
with col_csv:
    st.markdown("**Intercambio CSV**")
    st.caption("Carga de Datos / Backup")
    csv_data = df_f.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📝 Exportar CSV",
        data=csv_data,
        file_name=f"Backup_ISD_{filtro_nombre}.csv",
        mime="text/csv",
        use_container_width=True,
        help="Ideal para SISTEMAS. Archivo ligero de texto plano para integración con otras bases de datos."
    )

st.markdown("---")

# === GRAFICOS ===
st.markdown("### Analisis de Cartera")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Antigüedad", "Por Girador", "Exposicion", "Por Banco"]
)

with tab1:
    st.markdown(
        """
    <div style="background: var(--bg-card); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border-left: 3px solid var(--accent-amber);">
        <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 0;">
            <b>¿Qué muestra?</b> Distribución de documentos por días de vencimiento. 
            Colores más rojos = mayor riesgo de no cobrar.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    por_antiguedad = df_f.groupby("RANGO_DIAS")["IMPORTE"].sum().reset_index()
    por_antiguedad = por_antiguedad.sort_values("RANGO_DIAS")

    total_ant = por_antiguedad["IMPORTE"].sum()
    por_antiguedad["PORC"] = (por_antiguedad["IMPORTE"] / total_ant * 100).round(1)

    colores_map = {
        "Al dia": "#10b981",
        "1-30": "#3b82f6",
        "31-60": "#f59e0b",
        "61-90": "#f97316",
        "91-180": "#ef4444",
        "181-365": "#dc2626",
    }
    colores = [colores_map.get(str(r), "#64748b") for r in por_antiguedad["RANGO_DIAS"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=por_antiguedad["IMPORTE"],
            y=por_antiguedad["RANGO_DIAS"].astype(str),
            orientation="h",
            marker_color=colores,
            text=[
                f"S/. {v:,.0f} ({p}%)"
                for v, p in zip(por_antiguedad["IMPORTE"], por_antiguedad["PORC"])
            ],
            textposition="outside",
            textfont=dict(color="#f8fafc", size=11),
            hovertemplate="<b>%{y}</b><br>S/. %{x:,.0f}<br>(%{text})<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Antigüedad de Cartera",
            font=dict(color="#f8fafc", size=16, family="Inter"),
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            color="#64748b",
            tickfont=dict(color="#64748b"),
            gridcolor="rgba(255,255,255,0.03)",
            showline=False,
        ),
        yaxis=dict(
            color="#64748b", tickfont=dict(color="#f8fafc", size=12), showline=False
        ),
        margin=dict(t=50, b=40, l=100, r=40),
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown(
        """
    <div style="background: var(--bg-card); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border-left: 3px solid var(--accent-emerald);">
        <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 0;">
            <b>¿Qué muestra?</b> Top 10 deudores ordenados por monto. 
            Permite priorizar esfuerzos de cobranza por cliente.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    por_girador = (
        df_f.groupby("GIRADOR")
        .agg({"IMPORTE": "sum", "NUMERO UNICO": "count", "DIAS VENCIDOS": "max"})
        .reset_index()
        .sort_values("IMPORTE", ascending=False)
        .head(10)
    )
    total_gir = por_girador["IMPORTE"].sum()
    por_girador["PORC"] = (por_girador["IMPORTE"] / total_gir * 100).round(1)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=por_girador["IMPORTE"],
            y=por_girador["GIRADOR"],
            orientation="h",
            marker_color="#10b981",
            text=[f"S/. {v:,.0f}" for v in por_girador["IMPORTE"]],
            textposition="outside",
            textfont=dict(color="#f8fafc", size=10),
            hovertemplate="<b>%{y}</b><br>S/. %{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Top 10 Deudores (Giradores)",
            font=dict(color="#f8fafc", size=16, family="Inter"),
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            color="#64748b",
            tickfont=dict(color="#64748b"),
            gridcolor="rgba(255,255,255,0.03)",
            showline=False,
        ),
        yaxis=dict(
            color="#64748b",
            tickfont=dict(color="#f8fafc", size=10),
            showline=False,
            autorange="reversed",
        ),
        margin=dict(t=50, b=40, l=200, r=40),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown(
        """
    <div style="background: var(--bg-card); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border-left: 3px solid var(--accent-blue);">
        <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 0;">
            <b>¿Qué muestra?</b> Exposición de la cartera en soles y dólares. 
            Muestra el riesgo cambiario si el dólar sube o baja.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        por_moneda = df_f.groupby("MONEDA")["IMPORTE"].sum()
        total_mon = por_moneda.sum()

        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                labels=["SOLES", "DOLARES"],
                values=[por_moneda.get("SOLES", 0), por_moneda.get("DOLARES", 0)],
                hole=0.6,
                marker_colors=["#3b82f6", "#10b981"],
                textinfo="percent",
                textposition="outside",
                textfont=dict(color="#f8fafc", size=14),
                hovertemplate="<b>%{label}</b><br>S/. %{value:,.0f}<br>(%{percent})<extra></extra>",
            )
        )
        fig.update_layout(
            title=dict(
                text="Cartera por Moneda",
                font=dict(color="#f8fafc", size=14, family="Inter"),
                x=0.5,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(color="#94a3b8"),
            ),
            margin=dict(t=40, b=60, l=20, r=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        soles_usd = soles / tipo_cambio
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Cartera Total"],
                y=[soles_usd + dolares],
                marker_color="#3b82f6",
                text=f"$ {soles_usd + dolares:,.0f}",
                textposition="outside",
                textfont=dict(color="#f8fafc", size=14),
            )
        )
        fig.update_layout(
            title=dict(
                text=f"Equivalente USD (TC: S/. {tipo_cambio})",
                font=dict(color="#f8fafc", size=14, family="Inter"),
                x=0.5,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showline=False, showticklabels=False),
            yaxis=dict(
                color="#64748b",
                tickfont=dict(color="#64748b"),
                gridcolor="rgba(255,255,255,0.03)",
                showline=False,
            ),
            margin=dict(t=40, b=40, l=40, r=40),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
    <div style="background: var(--bg-card); border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
        <h4 style="color: var(--text-primary); margin: 0 0 1rem 0; font-size: 0.9rem;">Resumen de Exposicion</h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div style="text-align: center;">
                <p style="color: var(--text-muted); font-size: 0.7rem; margin: 0; text-transform: uppercase;">En Soles</p>
                <p style="color: var(--accent-blue); font-size: 1.25rem; font-weight: 700; margin: 0;">S/. {soles:,.0f}</p>
            </div>
            <div style="text-align: center;">
                <p style="color: var(--text-muted); font-size: 0.7rem; margin: 0; text-transform: uppercase;">En Dolares</p>
                <p style="color: var(--accent-emerald); font-size: 1.25rem; font-weight: 700; margin: 0;">$ {dolares:,.0f}</p>
            </div>
            <div style="text-align: center;">
                <p style="color: var(--text-muted); font-size: 0.7rem; margin: 0; text-transform: uppercase;">Total USD</p>
                <p style="color: var(--accent-amber); font-size: 1.25rem; font-weight: 700; margin: 0;">$ {total_usd:,.0f}</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with tab4:
    st.markdown(
        """
    <div style="background: var(--bg-card); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border-left: 3px solid var(--accent-blue);">
        <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 0;">
            <b>¿Qué muestra?</b> Distribución de cobranza por banco emisor. 
            Útil para negociar mejores tasas con los bancos más activos.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    por_banco = (
        df_f.groupby("BANCO")
        .agg({"IMPORTE": "sum", "NUMERO UNICO": "count"})
        .reset_index()
        .sort_values("IMPORTE", ascending=False)
    )
    total_banco = por_banco["IMPORTE"].sum()
    por_banco["PORC"] = (por_banco["IMPORTE"] / total_banco * 100).round(1)

    colores_banco = [
        "#3b82f6",
        "#10b981",
        "#f59e0b",
        "#8b5cf6",
        "#f43f5e",
        "#06b6d4",
        "#64748b",
    ]

    fig = go.Figure()
    bars = fig.add_trace(
        go.Bar(
            x=por_banco["BANCO"],
            y=por_banco["IMPORTE"],
            marker_color=colores_banco[: len(por_banco)],
            text=[
                f"S/. {v:,.0f}<br>({p}%)"
                for v, p in zip(por_banco["IMPORTE"], por_banco["PORC"])
            ],
            textposition="outside",
            textfont=dict(color="#f8fafc", size=10),
            hovertemplate="<b>%{x}</b><br>S/. %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Cartera por Banco",
            font=dict(color="#f8fafc", size=16, family="Inter"),
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            color="#64748b", tickfont=dict(color="#f8fafc", size=11), showline=False
        ),
        yaxis=dict(
            color="#64748b",
            tickfont=dict(color="#64748b"),
            gridcolor="rgba(255,255,255,0.03)",
            showline=False,
        ),
        margin=dict(t=50, b=80, l=50, r=30),
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === TOP GIRADORES ===
st.markdown("### Top 10 Giradores")

top_giradores = (
    df_f.groupby("GIRADOR")
    .agg({"IMPORTE": "sum", "NUMERO UNICO": "count", "DIAS VENCIDOS": "max"})
    .reset_index()
    .sort_values("IMPORTE", ascending=False)
    .head(10)
)
top_giradores.columns = ["Girador", "Monto (S/.)", "Docs", "Max Dias"]
top_giradores["Monto (S/.)"] = top_giradores["Monto (S/.)"].apply(
    lambda x: f"S/. {x:,.0f}"
)
top_giradores["Max Dias"] = top_giradores["Max Dias"].apply(
    lambda x: f"{x:.0f}d" if pd.notna(x) else "N/A"
)
st.dataframe(
    top_giradores,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Girador": st.column_config.TextColumn("Girador", width="large"),
        "Monto (S/.)": st.column_config.TextColumn("Monto", width="medium"),
        "Docs": st.column_config.NumberColumn("Docs", width="small"),
        "Max Dias": st.column_config.TextColumn("Max. Dias", width="small"),
    },
)

st.markdown("---")

# === TOP GIRADORES ===
st.markdown("### Top 10 Productos")

top_productos = (
    df_f.groupby("PRODUCTO")
    .agg({"IMPORTE": "sum", "NUMERO UNICO": "count", "DIAS VENCIDOS": "mean"})
    .reset_index()
    .sort_values("IMPORTE", ascending=False)
    .head(10)
)
top_productos.columns = ["Producto", "Monto (S/.)", "Docs", "Prom. Dias"]
top_productos["Monto (S/.)"] = top_productos["Monto (S/.)"].apply(
    lambda x: f"S/. {x:,.0f}"
)
top_productos["Prom. Dias"] = top_productos["Prom. Dias"].apply(
    lambda x: f"{x:.0f}d" if pd.notna(x) else "N/A"
)
st.dataframe(
    top_productos,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Producto": st.column_config.TextColumn("Producto", width="large"),
        "Monto (S/.)": st.column_config.TextColumn("Monto", width="medium"),
        "Docs": st.column_config.NumberColumn("Docs", width="small"),
        "Prom. Dias": st.column_config.TextColumn("Prom. Dias", width="small"),
    },
)

st.markdown("---")

# === TABLA DE DATOS ===
st.markdown("### Detalle de Documentos")

df_display = df_f[
    [
        "NUMERO UNICO",
        "GIRADOR",
        "Fecha de Vencimiento",
        "IMPORTE",
        "MONEDA",
        "DIAS VENCIDOS",
        "BANCO",
    ]
].copy()
df_display["Fecha de Vencimiento"] = pd.to_datetime(
    df_display["Fecha de Vencimiento"]
).dt.strftime("%d/%m/%Y")
df_display["IMPORTE"] = df_display["IMPORTE"].apply(lambda x: f"S/. {x:,.2f}")
df_display["DIAS VENCIDOS"] = df_display["DIAS VENCIDOS"].apply(
    lambda x: f"{x:.0f}" if pd.notna(x) else "N/A"
)
df_display.columns = [
    "Numero",
    "Girador",
    "Vencimiento",
    "Importe",
    "Moneda",
    "Dias",
    "Banco",
]

with st.expander("Ver todos los documentos"):
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

# === FOOTER ===
st.markdown(
    """
<div style="text-align: center; padding: 2rem 0; color: #64748b; font-size: 0.75rem;">
    Sueño Dorado - Control de Pagos ISD | Generado automaticamente
</div>
""",
    unsafe_allow_html=True,
)
