"""Tests de edge cases y boundary conditions."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.validator import DataValidator
from src.data.cleaner import DataCleaner


class TestEdgeCases:
    """Tests para casos límite."""

    def test_dataframe_vacio(self):
        df = pd.DataFrame(columns=['NUMERO UNICO', 'IMPORTE', 'BANCO', 'MONEDA', 
                                   'Fecha de Vencimiento', 'GIRADOR', 'ACEPTANTE', 
                                   'DOLARES', 'DIAS VENCIDOS'])
        validator = DataValidator(df)
        passed, results = validator.validate_all()
        assert len(results) >= 5, "Debe tener al menos 5 checks"

    def test_todos_los_campos_nulos(self):
        df = pd.DataFrame({
            'NUMERO UNICO': [None, None],
            'GIRADOR': [None, None],
            'ACEPTANTE': [None, None],
            'IMPORTE': [None, None],
            'MONEDA': [None, None],
            'BANCO': [None, None],
        })
        validator = DataValidator(df)
        passed, results = validator.validate_all()
        assert not passed, "Datos nulos deben fallar"

    def test_importe_exactamente_cero(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '002'],
            'IMPORTE': [0, 100],
            'MONEDA': ['SOLES', 'SOLES'],
            'BANCO': ['BCP', 'BCP'],
            'DOLARES': [0, 0],
            'DIAS VENCIDOS': [0, 0],
            'GIRADOR': ['A', 'B'],
            'ACEPTANTE': ['A', 'B'],
            'Fecha de Vencimiento': [datetime.now(), datetime.now()],
        })
        validator = DataValidator(df)
        validator.check_importe_positivo()
        assert validator.results[0].passed, "Importe cero es válido (no negativo)"

    def test_dias_vencidos_exactamente_365(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'DIAS VENCIDOS': [365],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'IMPORTE': [100],
            'DOLARES': [0],
            'GIRADOR': ['A'],
            'ACEPTANTE': ['A'],
            'Fecha de Vencimiento': [datetime.now()],
        })
        validator = DataValidator(df)
        validator.check_dias_vencidos_logico()
        assert validator.results[0].passed, "365 días debe ser válido"

    def test_dias_vencidos_366_falla(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'DIAS VENCIDOS': [366],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'IMPORTE': [100],
            'DOLARES': [0],
            'GIRADOR': ['A'],
            'ACEPTANTE': ['A'],
            'Fecha de Vencimiento': [datetime.now()],
        })
        validator = DataValidator(df)
        validator.check_dias_vencidos_logico()
        assert not validator.results[0].passed, "366 días debe fallar"

    def test_fecha_futura_valida(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'Fecha de Vencimiento': [datetime.now() + timedelta(days=365)],
            'IMPORTE': [100],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'DOLARES': [0],
            'DIAS VENCIDOS': [0],
            'GIRADOR': ['A'],
            'ACEPTANTE': ['A'],
        })
        validator = DataValidator(df)
        validator.check_fecha_vencimiento_valid()
        assert validator.results[0].passed, "Fecha futura debe ser válida"

    def test_nombres_validos_sin_duplicados(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '002'],
            'GIRADOR': ['EFACT SAC', 'MALBEZ S.R.LTDA'],
            'ACEPTANTE': ['BLACK', 'COLCHONES VIVE'],
            'IMPORTE': [1000, 2000],
            'MONEDA': ['SOLES', 'SOLES'],
            'BANCO': ['BCP', 'BBVA'],
            'DOLARES': [0, 0],
            'DIAS VENCIDOS': [0, 0],
            'Fecha de Vencimiento': [datetime.now(), datetime.now()],
            'PRODUCTO': ['DEUDA BANCOS', 'EFACT'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 2,
        })
        validator = DataValidator(df)
        passed, results = validator.validate_all()
        assert passed, "Nombres válidos deben pasar validación"

    def test_numeros_muy_grandes(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'IMPORTE': [999999999999],
            'DOLARES': [999999999],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'DIAS VENCIDOS': [0],
            'GIRADOR': ['A'],
            'ACEPTANTE': ['A'],
            'Fecha de Vencimiento': [datetime.now()],
        })
        validator = DataValidator(df)
        validator.check_importe_positivo()
        assert validator.results[0].passed, "Números grandes deben ser válidos"


class TestCalculations:
    """Tests para cálculos del dashboard."""

    def test_agrupar_por_mes(self):
        df = pd.DataFrame({
            'MES': ['2025-01', '2025-01', '2025-02', '2025-02', '2025-02'],
            'IMPORTE': [100, 200, 300, 400, 500],
        })
        resumen = df.groupby('MES')['IMPORTE'].sum()
        assert resumen['2025-01'] == 300
        assert resumen['2025-02'] == 1200

    def test_agrupar_por_semana(self):
        df = pd.DataFrame({
            'SEMANA': ['1', '1', '2', '2', '2'],
            'IMPORTE': [100, 200, 300, 400, 500],
        })
        resumen = df.groupby('SEMANA')['IMPORTE'].sum()
        assert resumen['1'] == 300
        assert resumen['2'] == 1200

    def test_filtro_multiple_bancos(self):
        df = pd.DataFrame({
            'BANCO': ['BCP', 'BBVA', 'BLACK', 'BCP', 'BBVA'],
            'IMPORTE': [100, 200, 300, 400, 500],
        })
        filtro = df[df['BANCO'].isin(['BCP', 'BBVA'])]
        assert len(filtro) == 4
        assert filtro['IMPORTE'].sum() == 1200

    def test_filtro_multiple_monedas(self):
        df = pd.DataFrame({
            'MONEDA': ['SOLES', 'DOLARES', 'SOLES', 'DOLARES'],
            'IMPORTE': [1000, 100, 2000, 200],
            'DOLARES': [0, 50, 0, 100],
        })
        filtro = df[df['MONEDA'].isin(['SOLES', 'DOLARES'])]
        assert len(filtro) == 4
        assert filtro['IMPORTE'].sum() == 3300
        assert filtro['DOLARES'].sum() == 150

    def test_vencidos_vs_no_vencidos(self):
        df = pd.DataFrame({
            'DIAS VENCIDOS': [0, 1, 30, 60, 90, -1],
            'IMPORTE': [100, 200, 300, 400, 500, 600],
        })
        vencidos = df[df['DIAS VENCIDOS'] > 0]
        no_vencidos = df[df['DIAS VENCIDOS'] <= 0]
        assert len(vencidos) == 4
        assert len(no_vencidos) == 2
        assert vencidos['IMPORTE'].sum() == 1400

    def test_promedio_dias_sin_nulos(self):
        df = pd.DataFrame({
            'DIAS VENCIDOS': [10, 20, 30, None, 50],
        })
        promedio = df['DIAS VENCIDOS'].mean()
        assert promedio == 27.5

    def test_suma_por_banco_y_moneda(self):
        df = pd.DataFrame({
            'BANCO': ['BCP', 'BCP', 'BBVA', 'BBVA'],
            'MONEDA': ['SOLES', 'DOLARES', 'SOLES', 'DOLARES'],
            'IMPORTE': [1000, 100, 2000, 200],
        })
        pivot = df.pivot_table(values='IMPORTE', index='BANCO', columns='MONEDA', aggfunc='sum')
        assert pivot.loc['BCP', 'SOLES'] == 1000
        assert pivot.loc['BCP', 'DOLARES'] == 100
        assert pivot.loc['BBVA', 'SOLES'] == 2000
        assert pivot.loc['BBVA', 'DOLARES'] == 200


class TestDataTypes:
    """Tests para tipos de datos."""

    def test_conversion_fecha_string(self):
        fechas_str = ['2025-01-15', '2025-02-20', 'invalid']
        fechas = pd.to_datetime(fechas_str, errors='coerce')
        assert fechas[0] == pd.Timestamp('2025-01-15')
        assert fechas[1] == pd.Timestamp('2025-02-20')
        assert pd.isna(fechas[2])

    def test_conversion_numero_string_con_comas(self):
        valores = ['1,000', '2,500.50', 'invalid', '3,141.59']
        numeros = pd.to_numeric([v.replace(',', '') for v in valores], errors='coerce')
        assert numeros[0] == 1000
        assert numeros[1] == 2500.50
        assert pd.isna(numeros[2])
        assert numeros[3] == 3141.59

    def test_tipos_consistentes_despues_filtro(self):
        df = pd.DataFrame({
            'IMPORTE': ['1000', '2000', '3000'],
        })
        df['IMPORTE'] = pd.to_numeric(df['IMPORTE'], errors='coerce')
        assert df['IMPORTE'].dtype in ['int64', 'float64']
        assert df['IMPORTE'].sum() == 6000
