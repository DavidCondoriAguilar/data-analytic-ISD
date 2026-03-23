"""Dashboard configuration and constants."""

import os
from pathlib import Path
from typing import Dict, List, Any

# Data configuration
DATA_PATH = os.environ.get('DATA_PATH', 'data/clean/datos_limpios.xlsx')

# Dashboard configuration
DASHBOARD_CONFIG = {
    'title': "Sueño Dorado - Control de Pagos",
    'subtitle': "Cartera de Cobranza | Dashboard Ejecutivo ISD",
    'icon': "💰",
    'layout': "wide"
}

# Color scheme
COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#3B82F6',
    'accent': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'bg_dark': '#0F172A',
    'bg_card': '#1E293B',
    'text': '#F8FAFC',
    'text_muted': '#94A3B8'
}

# Risk colors for charts
RISK_COLORS = {
    'Al día': '#10B981',
    '1-30 días': '#3B82F6',
    '31-60 días': '#F59E0B',
    '61-90 días': '#EF4444',
    '91-180 días': '#DC2626',
    '181-365 días': '#991B1B'
}

# Business validation rules
VALIDATION_RULES = {
    'monedas_validas': ['SOLES', 'DOLARES'],
    'bancos_validos': ['BBVA', 'BCP', 'BLACK'],
    'condicion_valida': ['PENDIENTE DE PAGO'],
    'dias_vencidos_max': 365,
    'monto_min': 0
}

# Risk classification
RISK_THRESHOLDS = {
    'alto_riesgo': 90,
    'medio_riesgo_min': 31,
    'medio_riesgo_max': 90,
    'bajo_riesgo_min': 1,
    'bajo_riesgo_max': 30
}

# Export columns
EXPORT_COLUMNS = [
    'NUMERO UNICO', 'Nº LETRA - FACT', 'GIRADOR', 'ACEPTANTE',
    'Fecha de Vencimiento', 'DIAS VENCIDOS', 'MONEDA', 'IMPORTE',
    'DOLARES', 'BANCO', 'PRODUCTO', 'CONDICION DEUDA'
]

# Period filters
PERIOD_FILTERS = {
    "1 Mes": 30,
    "2 Meses": 60,
    "3 Meses": 90,
    "6 Meses": 180,
    "Este Año": "year",
    "Todo": None
}

# Chart configuration
CHART_CONFIG = {
    'height': 400,
    'paper_bgcolor': '#1E293B',
    'plot_bgcolor': '#1E293B',
    'font_color': '#F8FAFC',
    'grid_color': 'rgba(255,255,255,0.1)'
}
