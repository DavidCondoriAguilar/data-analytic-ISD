"""Data processing and business logic for the dashboard."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional

from config import (
    DATA_PATH, VALIDATION_RULES, RISK_THRESHOLDS, 
    EXPORT_COLUMNS, PERIOD_FILTERS
)


@st.cache_data
def load_and_process_data() -> pd.DataFrame:
    """Load and process the raw data with 100% integrity."""
    df = pd.read_excel(DATA_PATH)
    
    # Strip whitespace from all string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
    
    # Filter pending payments - case insensitive and strip whitespace
    df = df[df['CONDICION DEUDA'].str.upper().str.strip() == 'PENDIENTE DE PAGO']
    
    # Convert data types - keep rows even if conversion fails (errors='coerce' creates NaN)
    df['Fecha de Vencimiento'] = pd.to_datetime(df['Fecha de Vencimiento'], errors='coerce')
    
    # Handle IMPORTE - works for both SOLES and DOLARES display
    df['IMPORTE'] = pd.to_numeric(df['IMPORTE'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce')
    
    # Handle DOLARES column - this is the actual USD amount
    df['DOLARES'] = pd.to_numeric(df['DOLARES'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce')
    
    # Handle DIAS VENCIDOS
    df['DIAS VENCIDOS'] = pd.to_numeric(df['DIAS VENCIDOS'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce')
    
    # Fill NaN numeric values with 0 to ensure totals match
    df['IMPORTE'] = df['IMPORTE'].fillna(0)
    df['DOLARES'] = df['DOLARES'].fillna(0)
    df['DIAS VENCIDOS'] = df['DIAS VENCIDOS'].fillna(0)
    
    # Create time dimensions
    df['MES'] = df['Fecha de Vencimiento'].dt.to_period('M').astype(str)
    df['SEMANA'] = df['Fecha de Vencimiento'].dt.isocalendar().week.astype(str)
    df['DIA'] = df['Fecha de Vencimiento'].dt.date
    df['TRIMESTRE'] = df['Fecha de Vencimiento'].dt.to_period('Q').astype(str)
    
    # Create risk classification
    df['RANGO_DIAS'] = pd.cut(
        df['DIAS VENCIDOS'], 
        bins=[-1, 0, 30, 60, 90, 180, 365],
        labels=['Al día', '1-30 días', '31-60 días', '61-90 días', '91-180 días', '181-365 días']
    )
    
    return df


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply all filters to the dataframe with comprehensive column coverage."""
    df_filtered = df.copy()
    
    # Core categorical filters - check each one precisely
    filter_mappings = {
        'bancos': 'BANCO',
        'monedas': 'MONEDA',
        'giradores': 'GIRADOR',
        'aceptantes': 'ACEPTANTE',
        'productos': 'PRODUCTO',
        'condiciones': 'CONDICION DEUDA',
        'rangos_dias': 'RANGO_DIAS'
    }
    
    # Apply each filter if it exists and has values
    for filter_key, column_name in filter_mappings.items():
        if filter_key in filters and filters[filter_key]:
            if column_name in df_filtered.columns:
                # Ensure exact matching with no partial matches
                df_filtered = df_filtered[df_filtered[column_name].isin(filters[filter_key])]
    
    # Date filters with precise handling
    if 'fecha_inicio' in filters and filters['fecha_inicio']:
        df_filtered = df_filtered[df_filtered['Fecha de Vencimiento'] >= pd.to_datetime(filters['fecha_inicio'])]
    
    if 'fecha_fin' in filters and filters['fecha_fin']:
        df_filtered = df_filtered[df_filtered['Fecha de Vencimiento'] <= pd.to_datetime(filters['fecha_fin'])]
    
    # Year filter
    if 'años' in filters and filters['años']:
        df_filtered = df_filtered[df_filtered['Fecha de Vencimiento'].dt.year.isin(filters['años'])]
    
    # Month filter
    if 'meses_num' in filters and filters['meses_num']:
        df_filtered = df_filtered[df_filtered['Fecha de Vencimiento'].dt.month.isin(filters['meses_num'])]
    
    return df_filtered


def get_period_dates(period: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Get start and end dates for a given period."""
    hoy = datetime.now().date()
    
    if period == "1 Mes":
        return hoy - timedelta(days=30), hoy
    elif period == "2 Meses":
        return hoy - timedelta(days=60), hoy
    elif period == "3 Meses":
        return hoy - timedelta(days=90), hoy
    elif period == "6 Meses":
        return hoy - timedelta(days=180), hoy
    elif period == "Este Año":
        return datetime(hoy.year, 1, 1).date(), hoy
    else:
        return None, None


def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate all business metrics."""
    # Basic metrics
    soles_total = df[df['MONEDA'] == 'SOLES']['IMPORTE'].sum()
    dolares_total = df[df['MONEDA'] == 'DOLARES']['DOLARES'].sum()
    total_docs = len(df)
    vencidos = len(df[df['DIAS VENCIDOS'] > 0])
    vencidos_monto = df[df['DIAS VENCIDOS'] > 0]['IMPORTE'].sum()
    al_dia = total_docs - vencidos
    al_dia_monto = df[df['DIAS VENCIDOS'] == 0]['IMPORTE'].sum()
    
    # Risk classification
    riesgo_alto = df[df['DIAS VENCIDOS'] > RISK_THRESHOLDS['alto_riesgo']]
    riesgo_medio = df[
        (df['DIAS VENCIDOS'] > RISK_THRESHOLDS['medio_riesgo_min']) & 
        (df['DIAS VENCIDOS'] <= RISK_THRESHOLDS['medio_riesgo_max'])
    ]
    riesgo_bajo = df[
        (df['DIAS VENCIDOS'] >= RISK_THRESHOLDS['bajo_riesgo_min']) & 
        (df['DIAS VENCIDOS'] <= RISK_THRESHOLDS['bajo_riesgo_max'])
    ]
    
    return {
        'soles_total': soles_total,
        'dolares_total': dolares_total,
        'total_docs': total_docs,
        'vencidos': vencidos,
        'vencidos_monto': vencidos_monto,
        'al_dia': al_dia,
        'al_dia_monto': al_dia_monto,
        'riesgo_alto': riesgo_alto,
        'riesgo_medio': riesgo_medio,
        'riesgo_bajo': riesgo_bajo,
        'pct_vencidos': (vencidos/total_docs*100) if total_docs > 0 else 0
    }


def get_filter_options(df: pd.DataFrame) -> Dict[str, list]:
    """Get available options for filters - scans ALL columns comprehensively."""
    filter_options = {}
    
    # Core categorical columns with dropdown filters
    categorical_columns = {
        'bancos': 'BANCO',
        'monedas': 'MONEDA', 
        'giradores': 'GIRADOR',
        'aceptantes': 'ACEPTANTE',
        'productos': 'PRODUCTO',
        'condiciones': 'CONDICION DEUDA',
        'rangos_dias': 'RANGO_DIAS'
    }
    
    # Scan each column and get unique values
    for key, column in categorical_columns.items():
        if column in df.columns:
            # Get unique values, drop NaN, sort, convert to list
            unique_vals = df[column].dropna().unique()
            filter_options[key] = sorted([str(v) for v in unique_vals if pd.notna(v)])
        else:
            filter_options[key] = []
    
    # Additional derived filters
    if 'Fecha de Vencimiento' in df.columns:
        # Get unique years
        years = df['Fecha de Vencimiento'].dt.year.dropna().unique()
        filter_options['años'] = sorted([int(y) for y in years if pd.notna(y)])
        
        # Get unique months
        months = df['Fecha de Vencimiento'].dt.month.dropna().unique()
        filter_options['meses_num'] = sorted([int(m) for m in months if pd.notna(m)])
    
    return filter_options


def validate_data_integrity(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate data integrity and business rules."""
    validations = []
    
    # Check unique IDs
    duplicados = df['NUMERO UNICO'].duplicated().sum()
    
    # Check null values
    nulos = df.isna().sum().sum()
    
    # Business validations
    monedas_validas = set(VALIDATION_RULES['monedas_validas'])
    monedas_ok = set(df['MONEDA'].unique()).issubset(monedas_validas)
    
    bancos_validos = set(VALIDATION_RULES['bancos_validos'])
    bancos_ok = set(df['BANCO'].unique()).issubset(bancos_validos)
    
    condicion_valida = set(VALIDATION_RULES['condicion_valida'])
    condicion_ok = set(df['CONDICION DEUDA'].dropna().unique()).issubset(condicion_valida)
    
    # Numeric validations
    imp_neg = (df['IMPORTE'] < 0).sum()
    dol_neg = (df['DOLARES'] < 0).sum()
    dias_neg = (df['DIAS VENCIDOS'] < 0).sum()
    dias_ext = (df['DIAS VENCIDOS'] > VALIDATION_RULES['dias_vencidos_max']).sum()
    
    return {
        'duplicados': duplicados,
        'nulos': nulos,
        'validaciones': [
            ('MONEDA', ', '.join(VALIDATION_RULES['monedas_validas']), list(df['MONEDA'].unique()), monedas_ok),
            ('BANCO', ', '.join(VALIDATION_RULES['bancos_validos']), list(df['BANCO'].unique()), bancos_ok),
            ('CONDICION DEUDA', ', '.join(VALIDATION_RULES['condicion_valida']), list(df['CONDICION DEUDA'].dropna().unique()), condicion_ok)
        ],
        'numeric_validations': {
            'importes_negativos': imp_neg,
            'dolares_negativos': dol_neg,
            'dias_negativos': dias_neg,
            'dias_excesivos': dias_ext
        }
    }


def prepare_export_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for export."""
    return df[EXPORT_COLUMNS].copy()


def get_summary_data(df: pd.DataFrame) -> pd.DataFrame:
    """Get summary data for certification."""
    resumen_data = {
        'Métrica': [
            'Total Documentos',
            'Total Cartera Soles',
            'Total Cartera Dólares',
            'Documentos al Día',
            'Documentos Vencidos',
            'Alto Riesgo (>90 días)',
            'Giradores Únicos',
            'Bancos',
            'Productos'
        ],
        'Valor': [
            f"{len(df)}",
            f"S/. {df['IMPORTE'].sum():,.2f}",
            f"$. {df['DOLARES'].sum():,.2f}",
            f"{len(df[df['DIAS VENCIDOS'] == 0])}",
            f"{len(df[df['DIAS VENCIDOS'] > 0])}",
            f"{len(df[df['DIAS VENCIDOS'] > 90])}",
            f"{df['GIRADOR'].nunique()}",
            f"{df['BANCO'].nunique()}",
            f"{df['PRODUCTO'].nunique()}"
        ]
    }
    return pd.DataFrame(resumen_data)
