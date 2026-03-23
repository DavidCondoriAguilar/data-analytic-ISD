"""Dashboard Sueño Dorado - Control de Pagos | Nivel Ejecutivo
Refactored Modular Architecture - Senior Level Implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import modular components
from config import DASHBOARD_CONFIG
from styles import get_dashboard_styles
from data_processor import (
    load_and_process_data, apply_filters, get_period_dates, 
    calculate_metrics, get_filter_options, validate_data_integrity
)
from components import (
    render_header, render_kpi_metrics, render_collection_status, 
    render_risk_indicators, render_sidebar, render_export_section, render_footer
)
from charts import render_charts_tabbed
from audit import render_audit_section

# Configure Streamlit page
st.set_page_config(
    page_title=DASHBOARD_CONFIG['title'], 
    layout=DASHBOARD_CONFIG['layout'], 
    page_icon=DASHBOARD_CONFIG['icon']
)

# Apply custom CSS
st.markdown(get_dashboard_styles(), unsafe_allow_html=True)

def main():
    """Main dashboard application."""
    
    # === HEADER ===
    render_header(DASHBOARD_CONFIG['title'], DASHBOARD_CONFIG['subtitle'])
    
    # === DATA LOADING ===
    df = load_and_process_data()
    
    # === SIDEBAR FILTERS ===
    filter_options = get_filter_options(df)
    filters = render_sidebar(df, filter_options)
    
    # === APPLY PERIOD FILTER ===
    fecha_inicio_periodo, fecha_fin_periodo = get_period_dates(filters['periodo'])
    
    # Prepare filter dict with ALL columns for precise filtering
    filter_dict = {
        'bancos': filters['bancos'],
        'monedas': filters['monedas'],
        'giradores': filters['giradores'],
        'aceptantes': filters.get('aceptantes', []),
        'productos': filters.get('productos', []),
        'rangos_dias': filters.get('rangos_dias', []),
        'fecha_inicio': fecha_inicio_periodo if fecha_inicio_periodo else filters['fecha_inicio'],
        'fecha_fin': fecha_fin_periodo if fecha_fin_periodo else filters['fecha_fin']
    }
    
    # === APPLY FILTERS ===
    df_filtered = apply_filters(df, filter_dict)
    
    # === CALCULATE METRICS ===
    metrics = calculate_metrics(df_filtered)
    
    # === RESUMEN EJECUTIVO ===
    st.markdown("""
    <div class="section-title">
        <h3>📋 Resumen Ejecutivo</h3>
        <p>Vista general de toda la cartera de cobranza - Muestra el total de documentos, montos en soles y dólares, y el estado de vencimiento.</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_kpi_metrics(metrics)
    
    st.markdown("---")
    
    # === ESTADO DE COBRANZA ===
    render_collection_status(metrics)
    
    st.markdown("---")
    
    # === INDICADORES DE RIESGO ===
    render_risk_indicators(df_filtered, metrics)
    
    st.markdown("---")
    
    # === GRÁFICOS PRINCIPALES ===
    render_charts_tabbed(df_filtered)
    
    st.markdown("---")
    
    # === DESCARGA ===
    render_export_section(df_filtered, metrics)
    
    st.markdown("---")
    
    # === AUDITORIA 100% MATCH ===
    with st.expander("🔍 VERIFICAR MATCH 100% CON DATA ORIGINAL", expanded=False):
        render_audit_section(df_filtered)
    
    # === FOOTER ===
    render_footer()

if __name__ == "__main__":
    main()
