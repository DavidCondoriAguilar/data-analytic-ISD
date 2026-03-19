"""Tests para módulo de validación de datos."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.validator import DataValidator, ValidationResult


@pytest.fixture
def df_limpio():
    return pd.DataFrame({
        'NUMERO UNICO': ['001', '002', '003'],
        'Nº LETRA - FACT': ['FACT E001-001', 'FACT E001-002', 'CUOTA 01 DE 12'],
        'GIRADOR': ['EFACT SAC', 'MALBEZ S.R.LTDA', 'PLANILLA - HABERES'],
        'ACEPTANTE': ['BLACK', 'COLCHONES VIVE', 'DREAM TEAM'],
        'Fecha de Vencimiento': [
            datetime.now() - timedelta(days=30),
            datetime.now() - timedelta(days=60),
            datetime.now() + timedelta(days=15)
        ],
        'DIAS VENCIDOS': [30, 60, 0],
        'IMPORTE': [5000.0, 10000.0, 7500.0],
        'MONEDA': ['SOLES', 'SOLES', 'DOLARES'],
        'BANCO': ['BCP', 'BBVA', 'BLACK'],
        'PRODUCTO': ['EFACT', 'DEUDA BANCOS', 'PLANILLA'],
        'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 3,
        'DOLARES': [0, 0, 1000.0]
    })


@pytest.fixture
def df_problemas():
    return pd.DataFrame({
        'NUMERO UNICO': ['001', '001', '003'],
        'GIRADOR': ['EFACT SAC', None, 'INVALID'],
        'ACEPTANTE': ['BLACK', 'BANCARIO', None],
        'Fecha de Vencimiento': ['fecha-invalida', datetime.now(), '2025-01-01'],
        'DIAS VENCIDOS': [-5, 60, 500],
        'IMPORTE': [-1000, 5000, 7500],
        'MONEDA': ['SOLES', 'BITCOIN', 'DOLARES'],
        'BANCO': ['BCP', 'BANCARIO', 'BBVA'],
        'DOLARES': [-100, 0, 1000],
        'PRODUCTO': ['EFACT', 'INVALIDO', 'DEUDA BANCOS'],
        'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 3,
    })


class TestDataValidator:
    def test_df_limpio_pasa(self, df_limpio):
        validator = DataValidator(df_limpio)
        passed, results = validator.validate_all()
        assert passed, f"Data limpia debería pasar. Fallidos: {[r for r in results if not r.passed]}"

    def test_df_con_problemas_falla(self, df_problemas):
        validator = DataValidator(df_problemas)
        passed, results = validator.validate_all()
        assert not passed

    def test_detecta_duplicados(self, df_problemas):
        validator = DataValidator(df_problemas)
        validator.check_no_duplicate_ids()
        assert not validator.results[0].passed
        assert validator.results[0].details['duplicates'] == 1

    def test_detecta_importes_negativos(self, df_problemas):
        validator = DataValidator(df_problemas)
        validator.check_importe_positivo()
        assert not validator.results[0].passed

    def test_report_genera_correctamente(self, df_limpio):
        validator = DataValidator(df_limpio)
        validator.validate_all()
        report = validator.get_report()
        assert 'confiabilidad' in report
        assert report['confiabilidad'] == '100.0%'
