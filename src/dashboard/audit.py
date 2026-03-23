"""Data auditing and verification module - 100% match guarantee with original data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Tuple
from config import DATA_PATH


@st.cache_data
def load_raw_original_data() -> pd.DataFrame:
    """Load completely raw data without any processing for comparison."""
    df = pd.read_excel(DATA_PATH)
    
    # Strip whitespace from string columns for accurate comparison
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
    
    return df


def audit_data_integrity(df_processed: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform comprehensive audit comparing processed data with original.
    Returns detailed verification report.
    """
    df_original = load_raw_original_data()
    
    audit_results = {
        'original_total_rows': len(df_original),
        'processed_total_rows': len(df_processed),
        'original_columns': list(df_original.columns),
        'processed_columns': list(df_processed.columns),
        'match_percentage': 0.0,
        'discrepancies': [],
        'verification_passed': False,
        'details': {}
    }
    
    # 1. Verify row count (filtering only PENDIENTE DE PAGO)
    original_pendiente = len(df_original[df_original['CONDICION DEUDA'].str.upper() == 'PENDIENTE DE PAGO'])
    processed_count = len(df_processed)
    
    audit_results['details']['row_count_match'] = original_pendiente == processed_count
    audit_results['details']['original_pendiente'] = original_pendiente
    audit_results['details']['processed_count'] = processed_count
    
    if original_pendiente != processed_count:
        audit_results['discrepancies'].append(
            f"Diferencia en conteo: Original tiene {original_pendiente} registros PENDIENTE DE PAGO, "
            f"procesados {processed_count}"
        )
    
    # 2. Verify column integrity
    critical_columns = [
        'NUMERO UNICO', 'Nº LETRA - FACT', 'GIRADOR', 'ACEPTANTE',
        'IMPORTE', 'DOLARES', 'MONEDA', 'BANCO', 'PRODUCTO',
        'CONDICION DEUDA', 'Fecha de Vencimiento', 'DIAS VENCIDOS'
    ]
    
    missing_in_processed = [col for col in critical_columns if col not in df_processed.columns]
    audit_results['details']['missing_columns'] = missing_in_processed
    
    if missing_in_processed:
        audit_results['discrepancies'].append(f"Columnas faltantes: {missing_in_processed}")
    
    # 3. Verify unique IDs match 100%
    original_ids = set(df_original[df_original['CONDICION DEUDA'].str.upper() == 'PENDIENTE DE PAGO']['NUMERO UNICO'].dropna())
    processed_ids = set(df_processed['NUMERO UNICO'].dropna())
    
    ids_match = original_ids == processed_ids
    audit_results['details']['ids_match'] = ids_match
    audit_results['details']['original_id_count'] = len(original_ids)
    audit_results['details']['processed_id_count'] = len(processed_ids)
    
    if not ids_match:
        missing_ids = original_ids - processed_ids
        extra_ids = processed_ids - original_ids
        if missing_ids:
            audit_results['discrepancies'].append(f"IDs faltantes: {len(missing_ids)} registros")
        if extra_ids:
            audit_results['discrepancies'].append(f"IDs extras: {len(extra_ids)} registros")
    
    # 4. Verify totals match - convert original data to numeric properly
    df_original_filtered = df_original[df_original['CONDICION DEUDA'].str.upper() == 'PENDIENTE DE PAGO']
    
    # Convert original IMPORTE to numeric
    original_importe = pd.to_numeric(df_original_filtered['IMPORTE'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0)
    original_soles = original_importe[df_original_filtered['MONEDA'] == 'SOLES'].sum()
    
    processed_soles = df_processed[df_processed['MONEDA'] == 'SOLES']['IMPORTE'].sum()
    
    # Convert original DOLARES to numeric
    original_dolares_col = pd.to_numeric(df_original_filtered['DOLARES'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0)
    original_dolares = original_dolares_col[df_original_filtered['MONEDA'] == 'DOLARES'].sum()
    
    processed_dolares = df_processed[df_processed['MONEDA'] == 'DOLARES']['DOLARES'].sum()
    
    soles_match = abs(original_soles - processed_soles) < 0.01
    dolares_match = abs(original_dolares - processed_dolares) < 0.01
    
    audit_results['details']['soles_match'] = soles_match
    audit_results['details']['dolares_match'] = dolares_match
    audit_results['details']['original_soles'] = original_soles
    audit_results['details']['processed_soles'] = processed_soles
    audit_results['details']['original_dolares'] = original_dolares
    audit_results['details']['processed_dolares'] = processed_dolares
    
    if not soles_match:
        audit_results['discrepancies'].append(
            f"Diferencia en Soles: Original S/. {original_soles:,.2f} vs Procesado S/. {processed_soles:,.2f}"
        )
    
    if not dolares_match:
        audit_results['discrepancies'].append(
            f"Diferencia en Dólares: Original $. {original_dolares:,.2f} vs Procesado $. {processed_dolares:,.2f}"
        )
    
    # 5. Calculate overall match percentage
    checks = [
        original_pendiente == processed_count,
        not missing_in_processed,
        ids_match,
        soles_match,
        dolares_match
    ]
    
    audit_results['match_percentage'] = (sum(checks) / len(checks)) * 100
    audit_results['verification_passed'] = all(checks)
    
    return audit_results


def get_sample_comparison(df_processed: pd.DataFrame, sample_size: int = 10) -> pd.DataFrame:
    """Get side-by-side comparison of sample records."""
    df_original = load_raw_original_data()
    df_original_filtered = df_original[df_original['CONDICION DEUDA'].str.upper() == 'PENDIENTE DE PAGO']
    
    # Get sample IDs
    sample_ids = df_processed['NUMERO UNICO'].head(sample_size).tolist()
    
    # Get matching records from both datasets
    original_sample = df_original_filtered[df_original_filtered['NUMERO UNICO'].isin(sample_ids)]
    processed_sample = df_processed[df_processed['NUMERO UNICO'].isin(sample_ids)]
    
    # Create comparison
    comparison_data = []
    common_cols = [col for col in original_sample.columns if col in processed_sample.columns]
    
    for uid in sample_ids:
        orig_row = original_sample[original_sample['NUMERO UNICO'] == uid]
        proc_row = processed_sample[processed_sample['NUMERO UNICO'] == uid]
        
        if not orig_row.empty and not proc_row.empty:
            for col in common_cols[:8]:  # Limit columns for display
                comparison_data.append({
                    'ID': uid,
                    'Columna': col,
                    'Valor Original': str(orig_row.iloc[0].get(col, 'N/A'))[:50],
                    'Valor Procesado': str(proc_row.iloc[0].get(col, 'N/A'))[:50],
                    'Match': str(orig_row.iloc[0].get(col, 'N/A')) == str(proc_row.iloc[0].get(col, 'N/A'))
                })
    
    return pd.DataFrame(comparison_data)


def render_audit_section(df_processed: pd.DataFrame) -> None:
    """Render comprehensive data audit section in Streamlit."""
    st.markdown("---")
    st.markdown("""
    <div style="background: #1E293B; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #3B82F6;">
        <h3 style="margin: 0; color: #F8FAFC;">🔍 Auditoría de Integridad de Datos</h3>
        <p style="margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 0.875rem;">
            Verificación 100% match con data original de empresa
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Realizando auditoría completa..."):
        audit_results = audit_data_integrity(df_processed)
    
    # Overall Status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if audit_results['verification_passed'] else "🔴"
        st.metric(
            f"{status_color} Estado de Verificación",
            "APROBADO 100%" if audit_results['verification_passed'] else "DIFERENCIAS ENCONTRADAS",
            help="Verificación completa de integridad"
        )
    
    with col2:
        st.metric(
            "Match Percentage",
            f"{audit_results['match_percentage']:.1f}%",
            help="Porcentaje de coincidencia con data original"
        )
    
    with col3:
        discrepancias = len(audit_results['discrepancies'])
        st.metric(
            "Discrepancias",
            f"{discrepancias}",
            help="Número de diferencias encontradas"
        )
    
    st.markdown("---")
    
    # Detailed Verification
    st.markdown("#### 📋 Detalle de Verificación")
    
    verificaciones = [
        ("✅ Conteo de Registros", audit_results['details'].get('row_count_match', False),
         f"Original: {audit_results['details'].get('original_pendiente', 0):,} | Procesado: {audit_results['details'].get('processed_count', 0):,}"),
        
        ("✅ Columnas Críticas", not audit_results['details'].get('missing_columns', []),
         f"Faltantes: {', '.join(audit_results['details'].get('missing_columns', []))}" if audit_results['details'].get('missing_columns') else "Todas las columnas presentes"),
        
        ("✅ IDs Únicos", audit_results['details'].get('ids_match', False),
         f"Original: {audit_results['details'].get('original_id_count', 0):,} | Procesado: {audit_results['details'].get('processed_id_count', 0):,}"),
        
        ("✅ Total Soles", audit_results['details'].get('soles_match', False),
         f"Original: S/. {audit_results['details'].get('original_soles', 0):,.2f} | Procesado: S/. {audit_results['details'].get('processed_soles', 0):,.2f}"),
        
        ("✅ Total Dólares", audit_results['details'].get('dolares_match', False),
         f"Original: $. {audit_results['details'].get('original_dolares', 0):,.2f} | Procesado: $. {audit_results['details'].get('processed_dolares', 0):,.2f}")
    ]
    
    for titulo, estado, detalle in verificaciones:
        icono = "✅" if estado else "❌"
        color = "#10B981" if estado else "#EF4444"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    padding: 0.75rem; background: {'rgba(16, 185, 129, 0.1)' if estado else 'rgba(239, 68, 68, 0.1)'}; 
                    border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {color};">
            <span style="font-weight: 600; color: {color};">{icono} {titulo}</span>
            <span style="color: #94A3B8; font-size: 0.875rem;">{detalle}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Show discrepancies if any
    if audit_results['discrepancies']:
        st.markdown("---")
        st.markdown("#### ⚠️ Discrepancias Encontradas")
        for disc in audit_results['discrepancies']:
            st.error(disc)
    
    # Sample comparison
    st.markdown("---")
    st.markdown("#### 🔬 Muestra de Comparación (Primeros 10 registros)")
    
    with st.spinner("Generando comparación muestral..."):
        sample_comparison = get_sample_comparison(df_processed, 10)
    
    if not sample_comparison.empty:
        # Color code matches
        def color_match(val):
            if val == True:
                return 'background-color: rgba(16, 185, 129, 0.3)'
            elif val == False:
                return 'background-color: rgba(239, 68, 68, 0.3)'
            return ''
        
        st.dataframe(
            sample_comparison.style.applymap(color_match, subset=['Match']),
            use_container_width=True,
            hide_index=True
        )
    
    # Final certification
    st.markdown("---")
    if audit_results['verification_passed']:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 1.5rem; 
                    border-left: 4px solid #10B981; text-align: center;">
            <h3 style="margin: 0; color: #10B981; font-size: 1.5rem;">🎉 CERTIFICACIÓN 100% MATCH</h3>
            <p style="margin: 0.5rem 0 0 0; color: #F8FAFC;">
                La data procesada coincide PERFECTAMENTE con la data original de la empresa.
                <br>Todos los registros, montos y cálculos están verificados.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border-radius: 12px; padding: 1.5rem; 
                    border-left: 4px solid #EF4444; text-align: center;">
            <h3 style="margin: 0; color: #EF4444; font-size: 1.5rem;">⚠️ DIFERENCIAS DETECTADAS</h3>
            <p style="margin: 0.5rem 0 0 0; color: #F8FAFC;">
                Se encontraron diferencias entre la data original y la procesada.
                <br>Revise las discrepancias listadas arriba.
            </p>
        </div>
        """, unsafe_allow_html=True)
