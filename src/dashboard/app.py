"""Dashboard Streamlit para Sueño Dorado - Moderno y Minimalista."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.data.audit import ConfiabilidadTracker

st.set_page_config(page_title="Sueño Dorado - Control de Pagos", layout="wide", page_icon="💰")

st.markdown("""
<style>
    /* === RESET & BASE === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1E3A5F;
        --secondary: #3B82F6;
        --accent: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --bg-dark: #0F172A;
        --bg-card: #1E293B;
        --text: #F8FAFC;
        --text-muted: #94A3B8;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    /* === HEADER === */
    .main-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 2rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* === KPI CARDS === */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: var(--secondary);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
    }
    
    .kpi-label {
        color: var(--text-muted);
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text);
        line-height: 1.2;
    }
    
    .kpi-value.positive { color: var(--accent); }
    .kpi-value.negative { color: var(--danger); }
    .kpi-value.neutral { color: var(--secondary); }
    
    .kpi-delta {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .kpi-delta.up { color: var(--accent); }
    .kpi-delta.down { color: var(--danger); }
    
    /* === CHART CARDS === */
    .chart-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* === METRICS ROW === */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-item {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-item .value {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--secondary);
    }
    
    .metric-item .label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
    }
    
    /* === STATUS BADGES === */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .badge.success {
        background: rgba(16, 185, 129, 0.2);
        color: var(--accent);
    }
    
    .badge.warning {
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning);
    }
    
    .badge.danger {
        background: rgba(239, 68, 68, 0.2);
        color: var(--danger);
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.2);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--secondary) !important;
        color: white !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--bg-dark);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* === STREAMLIT OVERRIDES === */
    .stMarkdown { color: var(--text); }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: var(--text-muted) !important;
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease forwards;
    }
</style>
""", unsafe_allow_html=True)


def format_number(num, prefix=""):
    if abs(num) >= 1_000_000:
        return f"{prefix}{num/1_000_000:.1f}M"
    elif abs(num) >= 1_000:
        return f"{prefix}{num/1_000:.1f}K"
    return f"{prefix}{num:,.0f}"


def get_trend_indicator(current, previous):
    if previous == 0:
        return "→", "neutral"
    pct = ((current - previous) / previous) * 100
    if pct > 0:
        return f"↑ {abs(pct):.1f}%", "up"
    elif pct < 0:
        return f"↓ {abs(pct):.1f}%", "down"
    return "→ 0%", "neutral"


@st.cache_data
def cargar_datos():
    import os
    excel_path = os.environ.get('DATA_PATH', 'data/clean/datos_limpios.xlsx')
    df = pd.read_excel(excel_path)
    
    df = df[df['CONDICION DEUDA'] == 'PENDIENTE DE PAGO']
    df['Fecha de Vencimiento'] = pd.to_datetime(df['Fecha de Vencimiento'], errors='coerce')
    df['IMPORTE'] = pd.to_numeric(df['IMPORTE'].astype(str).str.replace(',', ''), errors='coerce')
    df['DOLARES'] = pd.to_numeric(df['DOLARES'].astype(str).str.replace(',', ''), errors='coerce')
    df['DIAS VENCIDOS'] = pd.to_numeric(df['DIAS VENCIDOS'].astype(str).str.replace(',', ''), errors='coerce')
    
    df['MES'] = df['Fecha de Vencimiento'].dt.to_period('M').astype(str)
    df['SEMANA'] = df['Fecha de Vencimiento'].dt.isocalendar().week.astype(str)
    df['DIA'] = df['Fecha de Vencimiento'].dt.date
    df['TRIMESTRE'] = df['Fecha de Vencimiento'].dt.to_period('Q').astype(str)
    
    df['RANGO_DIAS'] = pd.cut(df['DIAS VENCIDOS'], 
                              bins=[-1, 0, 30, 60, 90, 180, 365],
                              labels=['Al día', '1-30', '31-60', '61-90', '91-180', '181-365'])
    
    return df


# === HEADER ===
st.markdown("""
<div class="main-header">
    <h1>💰 Sueño Dorado - Control de Pagos</h1>
    <p>Cartera de Cobranza | Dashboard Ejecutivo</p>
</div>
""", unsafe_allow_html=True)

# === SIDEBAR FILTERS ===
df = cargar_datos()

validator = DataValidator(df)
_, results = validator.validate_all()
report = validator.get_report()

with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    
    st.markdown("---")
    
    bancos = sorted(df['BANCO'].dropna().unique())
    filtro_banco = st.multiselect("Banco", options=bancos, default=bancos)
    
    monedas = sorted(df['MONEDA'].dropna().unique())
    filtro_moneda = st.multiselect("Moneda", options=monedas, default=monedas)
    
    giradores = sorted(df['GIRADOR'].dropna().unique())
    filtro_girador = st.multiselect("Girador", options=giradores, default=giradores)
    
    st.markdown("---")
    
    st.markdown("**Filtrar por Fechas:**")
    filtro_periodo = st.selectbox("Periodo:", 
        ["1 Mes", "2 Meses", "3 Meses", "6 Meses", "Este Año", "Todo"], 
        index=4)
    hoy = datetime.now().date()
    fecha_inicio = st.date_input("Desde", value=hoy - timedelta(days=365))
    fecha_fin = st.date_input("Hasta", value=hoy)
    
    st.markdown("---")
    
    st.markdown("### 📊 Estado del Sistema")
    conf = float(report['confiabilidad'].replace('%', ''))
    if conf >= 99.9:
        st.markdown('<span class="badge success">✓ Certificado 99.9%</span>', unsafe_allow_html=True)
    elif conf >= 95:
        st.markdown('<span class="badge warning">⚠ Verificar datos</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge danger">✗ Problemas detectados</span>', unsafe_allow_html=True)
    
    st.markdown(f"**Datos:** Certificados")
    st.markdown(f"**Total registros:** {len(df):,}")


# === APPLY FILTERS ===
df_f = df[
    (df['BANCO'].isin(filtro_banco)) & 
    (df['MONEDA'].isin(filtro_moneda)) &
    (df['GIRADOR'].isin(filtro_girador)) &
    (df['Fecha de Vencimiento'] >= pd.to_datetime(fecha_inicio)) &
    (df['Fecha de Vencimiento'] <= pd.to_datetime(fecha_fin))
].copy()

# === FILTRAR POR PERIODO (ATAJO) ===
if filtro_periodo == "1 Mes":
    fecha_limite = fecha_fin - timedelta(days=30)
elif filtro_periodo == "2 Meses":
    fecha_limite = fecha_fin - timedelta(days=60)
elif filtro_periodo == "3 Meses":
    fecha_limite = fecha_fin - timedelta(days=90)
elif filtro_periodo == "6 Meses":
    fecha_limite = fecha_fin - timedelta(days=180)
elif filtro_periodo == "Este Año":
    fecha_limite = datetime(fecha_fin.year, 1, 1).date()
else:
    fecha_limite = None

if fecha_limite:
    df_f = df_f[df_f['Fecha de Vencimiento'] >= pd.to_datetime(fecha_limite)]

# === CREAR COLUMNA PERIODO PARA GRÁFICO ===
df_f['PERIODO'] = df_f['MES']

# === AGREGAR SEGÚN PERIODO ===
df_periodo = df_f.groupby('PERIODO').agg({
    'NUMERO UNICO': 'count',
    'IMPORTE': 'sum',
    'DOLARES': 'sum',
    'DIAS VENCIDOS': 'mean'
}).reset_index()
df_periodo.columns = ['Periodo', 'Documentos', 'Total Soles', 'Total $', 'Prom. Días']
df_periodo = df_periodo.sort_values('Periodo')

# Formatear valores
df_periodo['Total Soles'] = df_periodo['Total Soles'].map('{:,.0f}'.format)
df_periodo['Total $'] = df_periodo['Total $'].map('{:,.0f}'.format)
df_periodo['Prom. Días'] = df_periodo['Prom. Días'].map('{:.0f}'.format)

# === KPI CARDS ===
soles_total = df_f[df_f['MONEDA'] == 'SOLES']['IMPORTE'].sum()
dolares_total = df_f[df_f['MONEDA'] == 'DOLARES']['DOLARES'].sum()
total_docs = len(df_f)
vencidos = len(df_f[df_f['DIAS VENCIDOS'] > 0])
vencidos_importe = df_f[df_f['DIAS VENCIDOS'] > 0]['IMPORTE'].sum()
al_dia = total_docs - vencidos
avg_dias = df_f['DIAS VENCIDOS'].mean()
max_dias = df_f['DIAS VENCIDOS'].max()

st.markdown("""
<div class="kpi-grid animate-in">
    <div class="kpi-card">
        <div class="kpi-label">Cartera Soles (S/)</div>
        <div class="kpi-value positive">S/. {:,.0f}</div>
        <div class="kpi-delta neutral">Total en SOLES</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Cartera Dólares ($)</div>
        <div class="kpi-value neutral">$ {:,.0f}</div>
        <div class="kpi-delta neutral">Total en DÓLARES</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Total Documentos</div>
        <div class="kpi-value">{:,}</div>
        <div class="kpi-delta neutral">{:,} al día · {:,} vencidos</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Cartera Vencida</div>
        <div class="kpi-value negative">S/. {:,.0f}</div>
        <div class="kpi-delta down">{} documentos vencidos</div>
    </div>
</div>
""".format(soles_total, dolares_total, total_docs, al_dia, vencidos, vencidos_importe, vencidos), unsafe_allow_html=True)

# === SECOND ROW KPIs ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Promedio Días Vencidos", f"{avg_dias:.0f}", delta=f"Máx: {max_dias:.0f}")
with col2:
    pct_vencido = (vencidos / total_docs * 100) if total_docs > 0 else 0
    st.metric("% Documentos Vencidos", f"{pct_vencido:.1f}%", delta=f"{vencidos} docs")
with col3:
    Giradores = int(df_f['GIRADOR'].nunique())
    st.metric("Giradores Únicos", Giradores)
with col4:
    Bancos = df_f['BANCO'].nunique()
    st.metric("Bancos", Bancos)

st.markdown("---")

# === TABLA RESUMEN POR PERIODO ===
st.markdown(f"### 📋 Resumen por {filtro_periodo}")
st.dataframe(df_periodo, use_container_width=True, hide_index=True)

st.markdown("---")

# === MAIN CHARTS ===
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Evolución", "🏦 Por Banco", "📊 Distribución", 
    "⚠️ Antigüedad", "👥 Por Girador", "📦 Por Producto"
])

with tab1:
    resumen = df_f.groupby('PERIODO')['IMPORTE'].sum().reset_index().sort_values('PERIODO')
    title = f"Evolución de Cartera ({filtro_periodo})"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=resumen['PERIODO'], 
        y=resumen['IMPORTE'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#3B82F6', width=3),
        fillcolor='rgba(59, 130, 246, 0.2)',
        marker=dict(size=8, color='#3B82F6', symbol='circle')
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#F8FAFC')),
        paper_bgcolor='#1E293B',
        plot_bgcolor='#1E293B',
        font=dict(color='#F8FAFC'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title=''),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title=''),
        height=400,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        banco_soles = df_f[df_f['MONEDA'] == 'SOLES'].groupby('BANCO')['IMPORTE'].sum().reset_index()
        fig1 = go.Figure(data=[go.Pie(
            labels=banco_soles['BANCO'],
            values=banco_soles['IMPORTE'],
            hole=0.6,
            marker=dict(colors=['#1E3A5F', '#3B82F6', '#10B981'])
        )])
        fig1.update_layout(
            title="Cartera en SOLES por Banco",
            paper_bgcolor='#1E293B',
            font=dict(color='#F8FAFC', size=12),
            height=350,
            annotations=[dict(text=f"S/. {soles_total/1_000_000:.1f}M", x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_b:
        banco_dolares = df_f[df_f['MONEDA'] == 'DOLARES'].groupby('BANCO')['DOLARES'].sum().reset_index()
        fig2 = go.Figure(data=[go.Pie(
            labels=banco_dolares['BANCO'],
            values=banco_dolares['DOLARES'],
            hole=0.6,
            marker=dict(colors=['#1E3A5F', '#3B82F6', '#10B981'])
        )])
        fig2.update_layout(
            title="Cartera en DÓLARES por Banco",
            paper_bgcolor='#1E293B',
            font=dict(color='#F8FAFC', size=12),
            height=350,
            annotations=[dict(text=f"$. {dolares_total/1_000_000:.1f}M", x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.markdown("#### Distribución por Aceptante")
        aceptante_data = df_f.groupby('ACEPTANTE')['IMPORTE'].sum().reset_index()
        aceptante_data = aceptante_data.sort_values('IMPORTE', ascending=False)
        fig3 = go.Figure(data=[go.Pie(
            labels=aceptante_data['ACEPTANTE'],
            values=aceptante_data['IMPORTE'],
            hole=0.5,
            marker=dict(colors=['#1E3A5F', '#3B82F6', '#10B981', '#F59E0B'])
        )])
        fig3.update_layout(
            title="Cartera por Aceptante",
            paper_bgcolor='#1E293B',
            font=dict(color='#F8FAFC', size=12),
            height=350
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        aceptante_det = df_f.groupby('ACEPTANTE').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum'
        }).reset_index()
        aceptante_det.columns = ['Aceptante', 'Docs', 'Total S/.']
        aceptante_det['%'] = (aceptante_det['Total S/.'] / aceptante_det['Total S/.'].sum() * 100).round(1)
        aceptante_det['Total S/.'] = aceptante_det['Total S/.'].map('{:,.0f}'.format)
        st.dataframe(aceptante_det, use_container_width=True, hide_index=True)
    
    with col_d:
        st.markdown("#### Distribución por Moneda")
        moneda_data = df_f.groupby('MONEDA').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum',
            'DOLARES': 'sum'
        }).reset_index()
        moneda_data.columns = ['Moneda', 'Docs', 'Total S/.', 'Total $']
        st.dataframe(moneda_data, use_container_width=True, hide_index=True)
        
        fig4 = go.Figure(go.Bar(
            x=['SOLES', 'DOLARES'],
            y=[soles_total, dolares_total],
            marker_color=['#3B82F6', '#10B981'],
            text=[f"S/. {soles_total/1_000_000:.1f}M", f"$. {dolares_total/1_000_000:.1f}M"],
            textposition='outside'
        ))
        fig4.update_layout(
            title="Cartera por Moneda",
            paper_bgcolor='#1E293B',
            plot_bgcolor='#1E293B',
            font=dict(color='#F8FAFC'),
            xaxis=dict(title=''),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Importe'),
            height=250,
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.markdown("#### Antigüedad de la Cartera")
    rango_data = df_f.groupby('RANGO_DIAS')['IMPORTE'].sum().reset_index()
    colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#DC2626', '#991B1B']
    
    fig5 = go.Figure()
    for i, (idx, row) in enumerate(rango_data.iterrows()):
        fig5.add_trace(go.Bar(
            x=[row['RANGO_DIAS']],
            y=[row['IMPORTE']],
            marker_color=colors[i % len(colors)],
            text=f"S/. {row['IMPORTE']/1_000_000:.1f}M",
            textposition='outside'
        ))
    
    fig5.update_layout(
        title="Cartera por Antigüedad (Días Vencidos)",
        paper_bgcolor='#1E293B',
        plot_bgcolor='#1E293B',
        font=dict(color='#F8FAFC'),
        xaxis=dict(title='', gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Importe'),
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("##### Detalle por Rango de Días")
    detalle_rango = df_f.groupby('RANGO_DIAS').agg({
        'NUMERO UNICO': 'count',
        'IMPORTE': 'sum'
    }).rename(columns={'NUMERO UNICO': 'Documentos'}).reset_index()
    detalle_rango['%'] = (detalle_rango['IMPORTE'] / detalle_rango['IMPORTE'].sum() * 100).round(1)
    detalle_rango['IMPORTE'] = detalle_rango['IMPORTE'].map('{:,.0f}'.format)
    st.dataframe(detalle_rango, use_container_width=True, hide_index=True)

with tab5:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### Top 10 Giradores por Importe")
        girador_imp = df_f.groupby('GIRADOR').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum',
            'DIAS VENCIDOS': 'mean'
        }).reset_index()
        girador_imp.columns = ['Girador', 'Docs', 'Total S/.', 'Prom. Días']
        girador_imp = girador_imp.sort_values('Total S/.', ascending=False).head(10)
        girador_imp['Total S/.'] = girador_imp['Total S/.'].map('{:,.0f}'.format)
        girador_imp['Prom. Días'] = girador_imp['Prom. Días'].map('{:.0f}'.format)
        st.dataframe(girador_imp, use_container_width=True, hide_index=True)
    
    with col_g2:
        st.markdown("#### Top 10 Giradores por Documentos")
        girador_docs = df_f.groupby('GIRADOR').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum'
        }).reset_index()
        girador_docs.columns = ['Girador', 'Docs', 'Total S/.']
        girador_docs = girador_docs.sort_values('Docs', ascending=False).head(10)
        st.dataframe(girador_docs, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### Análisis por Girador Específico")
    
    girador_select = st.selectbox("Selecciona Girador:", sorted(df_f['GIRADOR'].unique()))
    
    df_girador = df_f[df_f['GIRADOR'] == girador_select]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Documentos", len(df_girador))
    with col_g1:
        pass
    with c2:
        st.metric("Total S/.", f"S/. {df_girador['IMPORTE'].sum():,.0f}")
    with c3:
        st.metric("Total $", f"$ {df_girador['DOLARES'].sum():,.0f}")
    with c4:
        st.metric("Prom. Días", f"{df_girador['DIAS VENCIDOS'].mean():.0f}")
    
    st.markdown("##### Detalle de Documentos")
    cols_show = ['NUMERO UNICO', 'BANCO', 'MONEDA', 'IMPORTE', 'DOLARES', 'Fecha de Vencimiento', 'DIAS VENCIDOS', 'PRODUCTO']
    df_show = df_girador[cols_show].copy()
    df_show['IMPORTE'] = df_show['IMPORTE'].map('{:,.2f}'.format)
    df_show['DOLARES'] = df_show['DOLARES'].map('{:,.2f}'.format)
    df_show['Fecha de Vencimiento'] = pd.to_datetime(df_show['Fecha de Vencimiento']).dt.strftime('%Y-%m-%d')
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# === TAB 6: POR PRODUCTO ===
with tab6:
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("#### Por Producto (Importe)")
        producto_imp = df_f.groupby('PRODUCTO').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum',
            'DIAS VENCIDOS': 'mean'
        }).reset_index()
        producto_imp.columns = ['Producto', 'Docs', 'Total S/.', 'Prom. Días']
        producto_imp = producto_imp.sort_values('Total S/.', ascending=False)
        
        producto_imp_graf = producto_imp.copy()
        producto_imp['Total S/.'] = producto_imp['Total S/.'].map('{:,.0f}'.format)
        producto_imp['Prom. Días'] = producto_imp['Prom. Días'].map('{:.0f}'.format)
        st.dataframe(producto_imp, use_container_width=True, hide_index=True)
        
        fig_prod = go.Figure(go.Bar(
            x=producto_imp_graf['Producto'].values,
            y=producto_imp_graf['Total S/.'].values,
            marker_color='#3B82F6',
            text=producto_imp['Total S/.'].values,
            textposition='outside'
        ))
        fig_prod.update_layout(
            title="Cartera por Producto",
            paper_bgcolor='#1E293B',
            plot_bgcolor='#1E293B',
            font=dict(color='#F8FAFC'),
            xaxis=dict(title='', tickangle=45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='Importe'),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_prod, use_container_width=True)
    
    with col_p2:
        st.markdown("#### Por Producto (Documentos)")
        producto_docs = df_f.groupby('PRODUCTO').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum'
        }).reset_index()
        producto_docs.columns = ['Producto', 'Docs', 'Total S/.']
        producto_docs = producto_docs.sort_values('Docs', ascending=False)
        st.dataframe(producto_docs, use_container_width=True, hide_index=True)
        
        fig_prod2 = go.Figure(data=[go.Pie(
            labels=producto_docs['Producto'],
            values=producto_docs['Docs'],
            hole=0.5,
            marker=dict(colors=['#1E3A5F', '#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
        )])
        fig_prod2.update_layout(
            title="Documentos por Producto",
            paper_bgcolor='#1E293B',
            font=dict(color='#F8FAFC', size=12),
            height=300
        )
        st.plotly_chart(fig_prod2, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Análisis por Moneda")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("##### SOLES")
        soles_data = df_f[df_f['MONEDA'] == 'SOLES'].groupby('BANCO')['IMPORTE'].agg(['sum', 'count']).reset_index()
        soles_data.columns = ['Banco', 'Total S/.', 'Docs']
        soles_data['Promedio'] = (soles_data['Total S/.'] / soles_data['Docs']).map('{:,.0f}'.format)
        soles_data['Total S/.'] = soles_data['Total S/.'].map('{:,.0f}'.format)
        st.dataframe(soles_data, use_container_width=True, hide_index=True)
    
    with col_m2:
        st.markdown("##### DÓLARES")
        dolares_data = df_f[df_f['MONEDA'] == 'DOLARES'].groupby('BANCO')['DOLARES'].agg(['sum', 'count']).reset_index()
        dolares_data.columns = ['Banco', 'Total $', 'Docs']
        dolares_data['Promedio'] = (dolares_data['Total $'] / dolares_data['Docs']).map('{:,.0f}'.format)
        dolares_data['Total $'] = dolares_data['Total $'].map('{:,.0f}'.format)
        st.dataframe(dolares_data, use_container_width=True, hide_index=True)

st.markdown("---")

# === DATA TABLE ===
st.markdown("### 📋 Detalle de Registros")

def color_vencido(val):
    if val > 180:
        return 'background-color: #DC2626; color: white'
    elif val > 90:
        return 'background-color: #F59E0B; color: black'
    elif val > 30:
        return 'background-color: #FEF3C7; color: black'
    elif val > 0:
        return 'background-color: #FEF9C3; color: black'
    return ''

df_display = df_f[['NUMERO UNICO', 'GIRADOR', 'BANCO', 'MONEDA', 'IMPORTE', 'DOLARES', 
                   'Fecha de Vencimiento', 'DIAS VENCIDOS', 'PRODUCTO', 'ACEPTANTE']].copy()
df_display['IMPORTE'] = df_display['IMPORTE'].map('{:,.2f}'.format)
df_display['DOLARES'] = df_display['DOLARES'].map('{:,.2f}'.format)
df_display['Fecha de Vencimiento'] = pd.to_datetime(df_display['Fecha de Vencimiento']).dt.strftime('%Y-%m-%d')

st.dataframe(
    df_display.style.applymap(color_vencido, subset=['DIAS VENCIDOS']),
    use_container_width=True,
    height=400,
    hide_index=True
)

# === DOWNLOAD ===
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, f"reporte_sueno_dorado_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)

with col_dl2:
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_f.to_excel(writer, index=False, sheet_name='Datos')
    buffer.seek(0)
    st.download_button("📊 Descargar Excel", buffer, f"reporte_sueno_dorado_{datetime.now().strftime('%Y%m%d')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# === FOOTER ===
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #94A3B8; font-size: 0.75rem;'>Sueño Dorado - Control de Pagos | Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confiabilidad: {report['confiabilidad']}</div>", unsafe_allow_html=True)
