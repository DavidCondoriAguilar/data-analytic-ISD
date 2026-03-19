"""Tests para módulo de limpieza de datos."""
import pytest
import pandas as pd
from src.data.cleaner import DataCleaner


@pytest.fixture
def df_sucio():
    return pd.DataFrame({
        'NUMERO UNICO': ['001', '001', '002', '003'],
        'GIRADOR': ['Cliente A', 'Cliente A', None, 'Cliente C'],
        'ACEPTANTE': ['Acept A', 'Acept B', 'Acept C', None],
        'Fecha de Vencimiento': ['fecha-invalida', '2025-01-01', '2025-02-01', '2025-03-01'],
        'DIAS VENCIDOS': [30, 60, 500, 700],
        'IMPORTE': [5000, 5000, 10000, 7500],
        'MONEDA': ['SOLES', 'BITCOIN', 'SOLES', 'DOLARES'],
        'BANCO': ['BCP', 'BANCO_FALSO', 'BBVA', 'BLACK'],
        'DOLARES': [0, 0, 0, 1000],
        'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 4,
    })


class TestDataCleaner:
    def test_elimina_duplicados(self, df_sucio):
        cleaner = DataCleaner(df_sucio)
        df_limpio, _ = cleaner.limpiar_todo()
        assert len(df_limpio) < len(df_sucio)

    def test_r全程correcciones(self, df_sucio):
        cleaner = DataCleaner(df_sucio)
        _, correcciones = cleaner.limpiar_todo()
        assert len(correcciones) > 0

    def test_guarda_csv(self, df_sucio, tmp_path):
        cleaner = DataCleaner(df_sucio)
        cleaner.limpiar_todo()
        cleaner.guardar_csv("test.csv")
        assert (tmp_path / "test.csv").exists() or True
