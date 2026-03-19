"""Tests para el pipeline de limpieza."""
import pytest
import pandas as pd
from datetime import datetime
from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.data.cleaner import DataCleaner


class TestCleanPipeline:
    """Tests para el proceso completo de limpieza."""

    def test_loader_retorna_dataframe(self):
        loader = DataLoader()
        df = loader.cargar()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_loader_info_basica(self):
        loader = DataLoader()
        info = loader.cargar_info_basica()
        assert 'archivo' in info
        assert 'hoja' in info
        assert 'columnas' in info
        assert 'filas' in info
        assert info['filas'] > 0

    def test_cleaner_sin_cambios(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '002'],
            'GIRADOR': ['EFACT SAC', 'MALBEZ S.R.LTDA'],
            'ACEPTANTE': ['BLACK', 'COLCHONES VIVE'],
            'Fecha de Vencimiento': [datetime.now(), datetime.now()],
            'DIAS VENCIDOS': [10, 20],
            'IMPORTE': [1000, 2000],
            'MONEDA': ['SOLES', 'SOLES'],
            'BANCO': ['BCP', 'BBVA'],
            'DOLARES': [0, 0],
            'PRODUCTO': ['EFACT', 'DEUDA BANCOS'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 2,
        })
        cleaner = DataCleaner(df)
        df_limpio, correcciones = cleaner.limpiar_todo()
        assert len(df_limpio) == 2

    def test_cleaner_detecta_problemas(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '001'],
            'GIRADOR': ['EFACT SAC', None],
            'ACEPTANTE': ['BLACK', 'BANCARIO'],
            'Fecha de Vencimiento': ['invalid', datetime.now()],
            'DIAS VENCIDOS': [500, 20],
            'IMPORTE': [1000, 2000],
            'MONEDA': ['INVALID', 'SOLES'],
            'BANCO': ['FAKE', 'BBVA'],
            'DOLARES': [0, 0],
            'PRODUCTO': ['EFACT', 'INVALIDO'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 2,
        })
        cleaner = DataCleaner(df)
        df_limpio, correcciones = cleaner.limpiar_todo()
        assert len(correcciones) > 0

    def test_cleaner_metadata_agregada(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'GIRADOR': ['EFACT SAC'],
            'ACEPTANTE': ['BLACK'],
            'Fecha de Vencimiento': [datetime.now()],
            'DIAS VENCIDOS': [10],
            'IMPORTE': [1000],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'DOLARES': [0],
            'PRODUCTO': ['EFACT'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'],
        })
        cleaner = DataCleaner(df)
        df_limpio, _ = cleaner.limpiar_todo()
        assert '_limpieza_fecha' in df_limpio.columns
        assert '_limpieza_version' in df_limpio.columns

    def test_cleaner_guarda_csv(self, tmp_path):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'GIRADOR': ['EFACT SAC'],
            'ACEPTANTE': ['BLACK'],
            'Fecha de Vencimiento': [datetime.now()],
            'DIAS VENCIDOS': [10],
            'IMPORTE': [1000],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'DOLARES': [0],
            'PRODUCTO': ['EFACT'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'],
        })
        cleaner = DataCleaner(df)
        cleaner.limpiar_todo()
        cleaner.guardar_csv("test_output.csv")

    def test_cleaner_guarda_excel(self, tmp_path):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001'],
            'GIRADOR': ['EFACT SAC'],
            'ACEPTANTE': ['BLACK'],
            'Fecha de Vencimiento': [datetime.now()],
            'DIAS VENCIDOS': [10],
            'IMPORTE': [1000],
            'MONEDA': ['SOLES'],
            'BANCO': ['BCP'],
            'DOLARES': [0],
            'PRODUCTO': ['EFACT'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'],
        })
        cleaner = DataCleaner(df)
        cleaner.limpiar_todo()
        cleaner.guardar_excel("test_output.xlsx")

    def test_resumen_correcciones(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '002'],
            'GIRADOR': [None, 'MALBEZ S.R.LTDA'],
            'ACEPTANTE': ['COLCHONES VIVE', 'DREAM TEAM'],
            'Fecha de Vencimiento': [datetime.now(), datetime.now()],
            'DIAS VENCIDOS': [10, 20],
            'IMPORTE': [1000, 2000],
            'MONEDA': ['SOLES', 'SOLES'],
            'BANCO': ['BCP', 'BBVA'],
            'DOLARES': [0, 0],
            'PRODUCTO': ['EFACT', 'DEUDA BANCOS'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 2,
        })
        cleaner = DataCleaner(df)
        cleaner.limpiar_todo()
        resumen = cleaner.get_resumen_correcciones()
        assert 'total_correcciones' in resumen
        assert 'correcciones' in resumen

    def test_validacion_despues_limpieza(self):
        df = pd.DataFrame({
            'NUMERO UNICO': ['001', '001', '002'],
            'GIRADOR': ['EFACT SAC', 'MALBEZ S.R.LTDA', 'PLANILLA - HABERES'],
            'ACEPTANTE': ['BLACK', 'COLCHONES VIVE', 'DREAM TEAM'],
            'Fecha de Vencimiento': [datetime.now(), datetime.now(), datetime.now()],
            'DIAS VENCIDOS': [10, 20, 30],
            'IMPORTE': [1000, 2000, 3000],
            'MONEDA': ['SOLES', 'SOLES', 'DOLARES'],
            'BANCO': ['BCP', 'BBVA', 'BLACK'],
            'DOLARES': [0, 0, 500],
            'PRODUCTO': ['EFACT', 'DEUDA BANCOS', 'PLANILLA'],
            'CONDICION DEUDA': ['PENDIENTE DE PAGO'] * 3,
        })
        cleaner = DataCleaner(df)
        df_limpio, _ = cleaner.limpiar_todo()
        
        validator = DataValidator(df_limpio)
        passed, results = validator.validate_all()
        assert passed, f"Datos limpiados deben pasar validación. Fallidos: {[r for r in results if not r.passed]}"

    def test_pipeline_completo(self):
        loader = DataLoader()
        df = loader.cargar()
        
        validator = DataValidator(df)
        passed_before, _ = validator.validate_all()
        
        cleaner = DataCleaner(df)
        df_limpio, correcciones = cleaner.limpiar_todo()
        
        validator2 = DataValidator(df_limpio)
        passed_after, _ = validator2.validate_all()
        
        assert len(correcciones) > 0
        assert passed_after or not passed_before
