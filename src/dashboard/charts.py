"""Chart and visualization components for the dashboard."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from styles import get_info_box_html, get_success_box_html
from config import COLORS, RISK_COLORS, CHART_CONFIG


def create_evolution_chart(df: pd.DataFrame) -> None:
    """Create evolution chart for portfolio over time."""
    st.markdown(get_info_box_html(
        "📈 Evolución de Cartera",
        "Muestra cómo ha crecido la cartera de cobranza a lo largo del tiempo. Útil para identificar tendencias y meses con mayor deuda."
    ), unsafe_allow_html=True)
    
    evolucion = df.groupby('MES')['IMPORTE'].sum().reset_index().sort_values('MES')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evolucion['MES'], y=evolucion['IMPORTE'],
        mode='lines+markers', fill='tozeroy',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Evolución Mensual de Cartera",
        paper_bgcolor=CHART_CONFIG['paper_bgcolor'], 
        plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
        font=dict(color=CHART_CONFIG['font_color']), 
        height=CHART_CONFIG['height'],
        xaxis=dict(gridcolor=CHART_CONFIG['grid_color']),
        yaxis=dict(gridcolor=CHART_CONFIG['grid_color'], title='Monto (S/.)')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_bank_charts(df: pd.DataFrame) -> None:
    """Create bank distribution charts."""
    st.markdown(get_info_box_html(
        "🏦 Distribución por Banco",
        "Muestra qué porcentaje del total de deuda está en cada banco (BBVA, BCP, BLACK). Identifica dónde está el mayor riesgo de concentración."
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        banco_data = df.groupby('BANCO')['IMPORTE'].sum().reset_index()
        
        fig1 = go.Figure(data=[go.Pie(
            labels=banco_data['BANCO'],
            values=banco_data['IMPORTE'],
            hole=0.5,
            marker=dict(colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent']])
        )])
        
        fig1.update_layout(
            title="Por Banco (Soles)", 
            paper_bgcolor=CHART_CONFIG['paper_bgcolor'], 
            font=dict(color=CHART_CONFIG['font_color'])
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("##### Detalle por Banco")
        banco_det = df.groupby('BANCO').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum',
            'DIAS VENCIDOS': 'mean'
        }).reset_index()
        
        banco_det.columns = ['Banco', 'Docs', 'Monto S/.', 'Prom. Días']
        banco_det['%'] = (banco_det['Monto S/.'] / banco_det['Monto S/.'].sum() * 100).round(1)
        banco_det = banco_det.sort_values('Monto S/.', ascending=False)
        
        st.dataframe(banco_det, use_container_width=True, hide_index=True)


def create_girador_charts(df: pd.DataFrame) -> None:
    """Create girador (customer) debt charts."""
    st.markdown(get_info_box_html(
        "👥 Deuda por Girador",
        "Identifica a los clientes (giradores) con mayor monto de deuda. Los top 5 representan la mayor concentración de riesgo."
    ), unsafe_allow_html=True)
    
    girador_data = df.groupby('GIRADOR')['IMPORTE'].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig = go.Figure(go.Bar(
        x=girador_data['IMPORTE'],
        y=girador_data['GIRADOR'],
        orientation='h',
        marker_color=COLORS['secondary']
    ))
    
    fig.update_layout(
        title="Top 10 Giradores por Deuda",
        paper_bgcolor=CHART_CONFIG['paper_bgcolor'], 
        plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
        font=dict(color=CHART_CONFIG['font_color']), 
        height=CHART_CONFIG['height'],
        xaxis=dict(gridcolor=CHART_CONFIG['grid_color']),
        yaxis=dict(title='')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("##### Tabla de Giradores")
    girador_det = df.groupby('GIRADOR').agg({
        'NUMERO UNICO': 'count',
        'IMPORTE': 'sum',
        'DIAS VENCIDOS': 'mean'
    }).reset_index()
    
    girador_det.columns = ['Girador', 'Docs', 'Monto S/.', 'Prom. Días']
    girador_det = girador_det.sort_values('Monto S/.', ascending=False)
    
    st.dataframe(girador_det, use_container_width=True, hide_index=True)


def create_producto_charts(df: pd.DataFrame) -> None:
    """Create product distribution charts."""
    st.markdown(get_info_box_html(
        "📦 Deuda por Producto",
        "Clasificación de la deuda según el tipo de producto o servicio. DEUDA BANCOS es la más grande."
    ), unsafe_allow_html=True)
    
    prod_data = df.groupby('PRODUCTO')['IMPORTE'].sum().sort_values(ascending=False).reset_index()
    
    fig = go.Figure(go.Bar(
        x=prod_data['PRODUCTO'],
        y=prod_data['IMPORTE'],
        marker_color=COLORS['accent'],
        text=prod_data['IMPORTE'].map('{:,.0f}'.format),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Cartera por Producto",
        paper_bgcolor=CHART_CONFIG['paper_bgcolor'], 
        plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
        font=dict(color=CHART_CONFIG['font_color']), 
        height=350,
        xaxis=dict(title='', tickangle=45),
        yaxis=dict(gridcolor=CHART_CONFIG['grid_color'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    prod_det = df.groupby('PRODUCTO').agg({
        'NUMERO UNICO': 'count',
        'IMPORTE': 'sum'
    }).reset_index()
    
    prod_det.columns = ['Producto', 'Docs', 'Monto S/.']
    prod_det['%'] = (prod_det['Monto S/.'] / prod_det['Monto S/.'].sum() * 100).round(1)
    
    st.dataframe(prod_det, use_container_width=True, hide_index=True)


def create_antiguedad_charts(df: pd.DataFrame) -> None:
    """Create debt age charts."""
    st.markdown(get_info_box_html(
        "⏰ Antigüedad de la Deuda",
        "Clasifica las deudas según días vencidos. Deudas más antiguas son más difíciles de cobrar."
    ), unsafe_allow_html=True)
    
    rango_data = df.groupby('RANGO_DIAS')['IMPORTE'].sum().reset_index()
    
    fig = go.Figure()
    for idx, row in rango_data.iterrows():
        fig.add_trace(go.Bar(
            x=[row['RANGO_DIAS']],
            y=[row['IMPORTE']],
            marker_color=RISK_COLORS.get(str(row['RANGO_DIAS']), COLORS['secondary']),
            text=f"S/. {row['IMPORTE']/1_000_000:.1f}M",
            textposition='outside'
        ))
    
    fig.update_layout(
        title="Cartera por Antigüedad",
        paper_bgcolor=CHART_CONFIG['paper_bgcolor'], 
        plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
        font=dict(color=CHART_CONFIG['font_color']), 
        height=350,
        xaxis=dict(title=''), 
        yaxis=dict(title='Monto (S/.)'),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    rango_det = df.groupby('RANGO_DIAS').agg({
        'NUMERO UNICO': 'count',
        'IMPORTE': 'sum'
    }).reset_index()
    
    rango_det.columns = ['Rango Días', 'Docs', 'Monto S/.']
    rango_det['%'] = (rango_det['Monto S/.'] / rango_det['Monto S/.'].sum() * 100).round(1)
    
    st.dataframe(rango_det, use_container_width=True, hide_index=True)


def create_certification_details(df: pd.DataFrame) -> None:
    """Create certification detail tables."""
    st.markdown(get_info_box_html(
        "📋 DETALLE PARA VERIFICACIÓN",
        "Datos desglosados para que puedas verificar manualmente si lo deseas."
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Por Banco")
        banco_det = df.groupby('BANCO').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': ['sum', 'mean', 'max']
        }).reset_index()
        
        banco_det.columns = ['Banco', 'Docs', 'Total S/.', 'Promedio', 'Máximo']
        st.dataframe(banco_det, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("##### Por Moneda")
        moneda_det = df.groupby('MONEDA').agg({
            'NUMERO UNICO': 'count',
            'IMPORTE': 'sum',
            'DOLARES': 'sum'
        }).reset_index()
        
        moneda_det.columns = ['Moneda', 'Docs', 'Soles', 'Dólares']
        st.dataframe(moneda_det, use_container_width=True, hide_index=True)


def render_charts_tabbed(df: pd.DataFrame) -> None:
    """Render all charts in tabbed interface."""
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Evolución", "🏦 Por Banco", "👥 Por Girador", "📦 Por Producto", "⏰ Antigüedad", "✅ Certificación"
    ])
    
    with tab1:
        create_evolution_chart(df)
    
    with tab2:
        create_bank_charts(df)
    
    with tab3:
        create_girador_charts(df)
    
    with tab4:
        create_producto_charts(df)
    
    with tab5:
        create_antiguedad_charts(df)
    
    with tab6:
        from components import render_certification_section
        from data_processor import validate_data_integrity, get_summary_data
        
        validation_results = validate_data_integrity(df)
        render_certification_section(df, validation_results)
        
        st.markdown("---")
        
        # Summary data
        st.markdown(get_success_box_html(
            "📊 RESUMEN EJECUTIVO CERTIFICADO",
            ""
        ), unsafe_allow_html=True)
        
        summary_df = get_summary_data(df)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        create_certification_details(df)
