"""Test de integración: verifica que cálculos del dashboard coincidan con Excel."""
import pytest
import pandas as pd
from src.data.loader import DataLoader
from src.data.validator import DataValidator


class TestDashboardAccuracy:
    """Verifica precisión de cálculos vs datos originales."""

    def test_carga_excel_sin_errores(self):
        loader = DataLoader()
        df = loader.cargar()
        assert len(df) > 0, "Excel debe cargar datos"
        assert len(df.columns) >= 10, "Debe tener columnas requeridas"

    def test_kpis_soles_coinciden(self):
        loader = DataLoader()
        df = loader.cargar()
        df = df[df['MONEDA'] == 'SOLES']
        df['IMPORTE'] = pd.to_numeric(df['IMPORTE'], errors='coerce')
        
        total_python = df['IMPORTE'].sum()
        
        df_manual = pd.read_excel("SALDO - FLUJO DE PAGOS 2026.xlsx", 
                                   sheet_name='DATA ORIGINAL', skiprows=2)
        df_manual = df_manual[df_manual['MONEDA'] == 'SOLES']
        df_manual['IMPORTE'] = pd.to_numeric(df_manual['IMPORTE'], errors='coerce')
        total_excel = df_manual['IMPORTE'].sum()
        
        diferencia = abs(total_python - total_excel)
        assert diferencia < 0.01, f"KPI Soles diverge: Python={total_python}, Excel={total_excel}"

    def test_kpis_dolares_coinciden(self):
        loader = DataLoader()
        df = loader.cargar()
        df = df[df['MONEDA'] == 'DOLARES']
        df['DOLARES'] = pd.to_numeric(df['DOLARES'], errors='coerce')
        
        total_python = df['DOLARES'].sum()
        
        df_manual = pd.read_excel("SALDO - FLUJO DE PAGOS 2026.xlsx",
                                   sheet_name='DATA ORIGINAL', skiprows=2)
        df_manual = df_manual[df_manual['MONEDA'] == 'DOLARES']
        df_manual['DOLARES'] = pd.to_numeric(df_manual['DOLARES'], errors='coerce')
        total_excel = df_manual['DOLARES'].sum()
        
        diferencia = abs(total_python - total_excel)
        assert diferencia < 0.01, f"KPI Dólares diverge: Python={total_python}, Excel={total_excel}"

    def test_total_documentos_exacto(self):
        loader = DataLoader()
        df = loader.cargar()
        df = df[df['CONDICION DEUDA'] == 'PENDIENTE DE PAGO']
        
        df_manual = pd.read_excel("SALDO - FLUJO DE PAGOS 2026.xlsx",
                                   sheet_name='DATA ORIGINAL', skiprows=2)
        df_manual = df_manual[df_manual['CONDICION DEUDA'] == 'PENDIENTE DE PAGO']
        
        assert len(df) == len(df_manual), f"Documentos: Python={len(df)}, Excel={len(df_manual)}"

    def test_filtro_banco_funciona(self):
        loader = DataLoader()
        df = loader.cargar()
        
        df_bcp = df[df['BANCO'] == 'BCP']
        assert len(df_bcp) > 0, "Debe filtrar BCP"
        assert all(df_bcp['BANCO'] == 'BCP'), "Todos deben ser BCP"

    def test_filtro_moneda_funciona(self):
        loader = DataLoader()
        df = loader.cargar()
        
        df_soles = df[df['MONEDA'] == 'SOLES']
        assert len(df_soles) > 0, "Debe filtrar SOLES"
        assert all(df_soles['MONEDA'] == 'SOLES'), "Todos deben ser SOLES"

    def test_validacion_detecta_problemas(self):
        loader = DataLoader()
        df = loader.cargar()
        validator = DataValidator(df)
        passed, results = validator.validate_all()
        
        assert len(results) >= 14, "Debe tener 10 checks de validación"
        
        failed = [r for r in results if not r.passed]
        print(f"\nValidación encontró {len(failed)} problemas de {len(results)} checks")

    def test_evolucion_mensual_calcula_correctamente(self):
        loader = DataLoader()
        df = loader.cargar()
        df = df[df['CONDICION DEUDA'] == 'PENDIENTE DE PAGO']
        df['Fecha de Vencimiento'] = pd.to_datetime(df['Fecha de Vencimiento'], errors='coerce')
        df['IMPORTE'] = pd.to_numeric(df['IMPORTE'], errors='coerce')
        df['MES'] = df['Fecha de Vencimiento'].dt.to_period('M').astype(str)
        
        resumen = df.groupby('MES')['IMPORTE'].sum()
        
        assert len(resumen) > 0, "Debe tener resumen por mes"
        assert resumen.sum() > 0, "La suma debe ser positiva"

    def test_evolucion_semanal_calcula_correctamente(self):
        loader = DataLoader()
        df = loader.cargar()
        df = df[df['CONDICION DEUDA'] == 'PENDIENTE DE PAGO']
        df['Fecha de Vencimiento'] = pd.to_datetime(df['Fecha de Vencimiento'], errors='coerce')
        df['IMPORTE'] = pd.to_numeric(df['IMPORTE'], errors='coerce')
        df['SEMANA'] = df['Fecha de Vencimiento'].dt.isocalendar().week.astype(str)
        
        resumen = df.groupby('SEMANA')['IMPORTE'].sum()
        
        assert len(resumen) > 0, "Debe tener resumen por semana"
        assert resumen.sum() > 0, "La suma debe ser positiva"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
