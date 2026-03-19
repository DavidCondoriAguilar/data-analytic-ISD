"""Módulo de limpieza y corrección de datos."""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Tuple, List
from config.settings import (
    DATA_CLEAN_DIR, MONEDAS_VALIDAS, BANCOS_VALIDOS, BASE_DIR,
    ACEPTANTES_VALIDOS, PRODUCTOS_VALIDOS, GIRADORES_VALIDOS
)


class DataCleaner:
    """Limpia y corrige datos problemáticos."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.correcciones: List[dict] = []

    def limpiar_todo(self) -> Tuple[pd.DataFrame, List[dict]]:
        self._strip_espacios()
        self._eliminar_filas_encabezado()
        self._crear_id_unico_si_falta()
        self._validar_importe_numerico()
        self._corregir_duplicados()
        self._corregir_fechas_invalidas()
        self._corregir_dias_vencidos_extremos()
        self._corregir_nulos_girador()
        self._corregir_nulos_aceptante()
        self._corregir_monedas_invalidas()
        self._corregir_bancos_invalidos()
        self._corregir_aceptantes_invalidos()
        self._corregir_productos_invalidos()
        self._convertir_tipos_numericos()
        self._eliminar_columnas_innecesarias()
        self._ordenar_columnas()
        self._agregar_metadata()
        return self.df, self.correcciones

    def _strip_espacios(self):
        """Elimina espacios al inicio y final de todos los valores de texto"""
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df.loc[:, col] = self.df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )

    def _eliminar_columnas_innecesarias(self):
        """Elimina columnas vacías o innecesarias"""
        columnas_a_eliminar = []
        
        for col in self.df.columns:
            if col.startswith('_'):
                continue
            valores_unicos = self.df[col].dropna().unique()
            if len(valores_unicos) == 0:
                columnas_a_eliminar.append(col)
            elif col in ['FP', 'Columna1', 'Columna1', 'Unnamed']:
                columnas_a_eliminar.append(col)
        
        if columnas_a_eliminar:
            self.df = self.df.drop(columns=columnas_a_eliminar)
            self._agregar_correccion("COLUMNAS_ELIMINADAS", f"Eliminadas columnas: {columnas_a_eliminar}", len(columnas_a_eliminar))

    def _ordenar_columnas(self):
        """Ordena columnas de forma lógica"""
        columnas_ordenadas = ['NUMERO UNICO', 'Nº LETRA - FACT', 'GIRADOR', 'ACEPTANTE', 
                              'Fecha de Vencimiento', 'DIAS VENCIDOS', 'MONEDA', 'IMPORTE', 
                              'DOLARES', 'BANCO', 'PRODUCTO', 'CONDICION DEUDA']
        columnas_existentes = [c for c in columnas_ordenadas if c in self.df.columns]
        otras = [c for c in self.df.columns if c not in columnas_ordenadas and not c.startswith('_')]
        self.df = self.df[columnas_existentes + otras]

    def _agregar_correccion(self, tipo: str, descripcion: str, cantidad: int):
        self.correcciones.append({
            "tipo": tipo,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "timestamp": datetime.now().isoformat()
        })

    def _eliminar_filas_encabezado(self):
        """Elimina filas que son encabezados repetidos (IMPORTE=IMPORTE, MONEDA=MONEDA, etc)"""
        if 'IMPORTE' not in self.df.columns:
            return
        filas_encabezado = (
            (self.df['IMPORTE'] == 'IMPORTE') | 
            (self.df['IMPORTE'] == 'NUMERO UNICO') |
            (self.df.get('GIRADOR', pd.Series()) == 'GIRADOR')
        )
        cantidad = filas_encabezado.sum()
        if cantidad > 0:
            self.df = self.df[~filas_encabezado]
            self._agregar_correccion("FILAS_ENCABEZADO", f"Eliminadas {cantidad} filas de encabezado repetido", cantidad)

    def _crear_id_unico_si_falta(self):
        """Crea ID único si NUMERO UNICO está vacío o es duplicado"""
        if 'NUMERO UNICO' not in self.df.columns:
            self.df['NUMERO UNICO'] = range(1, len(self.df) + 1)
            self._agregar_correccion("ID_CREADO", "Creado ID único secuencial", len(self.df))
            return
        
        vacios = self.df['NUMERO UNICO'].isna() | (self.df['NUMERO UNICO'] == 'NUMERO UNICO')
        if vacios.any():
            cantidad = vacios.sum()
            self.df.loc[vacios, 'NUMERO UNICO'] = range(len(self.df[vacios]))
            self._agregar_correccion("ID_CREADO", f"Creados {cantidad} IDs únicos para registros sin ID", cantidad)

    def _validar_importe_numerico(self):
        """Valida que IMPORTE sea numérico, de lo contrario lo elimina o corrige"""
        if 'IMPORTE' not in self.df.columns:
            return
        no_numerico = ~pd.to_numeric(self.df['IMPORTE'], errors='coerce').notna()
        cantidad = no_numerico.sum()
        if cantidad > 0:
            self.df = self.df[pd.to_numeric(self.df['IMPORTE'], errors='coerce').notna()]
            self._agregar_correccion("IMPORTE_INVALIDO", f"Eliminadas {cantidad} filas con IMPORTE no numérico", cantidad)

    def _corregir_duplicados(self):
        col = 'NUMERO UNICO'
        if col not in self.df.columns:
            return
        duplicados = self.df[col].duplicated()
        if duplicados.any():
            cantidad = duplicados.sum()
            self.df = self.df[~duplicados]
            self._agregar_correccion("DUPLICADOS", f"Eliminados {cantidad} registros duplicados", cantidad)

    def _corregir_fechas_invalidas(self):
        col = 'Fecha de Vencimiento'
        if col not in self.df.columns:
            return
        fechas = pd.to_datetime(self.df[col], errors='coerce')
        invalidas = fechas.isna()
        cantidad = invalidas.sum()
        if cantidad > 0:
            self.df.loc[invalidas, col] = pd.Timestamp.now()
            self._agregar_correccion("FECHAS_INVÁLIDAS", f"Corregidas {cantidad} fechas inválidas", cantidad)

    def _corregir_dias_vencidos_extremos(self):
        col = 'DIAS VENCIDOS'
        if col not in self.df.columns:
            return
        valores = pd.to_numeric(self.df[col], errors='coerce')
        extremos = valores > 365
        cantidad = extremos.sum()
        if cantidad > 0:
            self.df.loc[extremos, col] = 365
            self._agregar_correccion("DÍAS_EXTREMOS", f"Limitados {cantidad} valores a 365 días", cantidad)

    def _corregir_nulos_girador(self):
        col = 'GIRADOR'
        if col not in self.df.columns:
            return
        nulos = self.df[col].isna()
        cantidad = nulos.sum()
        if cantidad > 0:
            self.df.loc[nulos, col] = 'SIN GIRADOR'
            self._agregar_correccion("GIRADOR_NULO", f"Rellenados {cantidad} giradores nulos", cantidad)

    def _corregir_nulos_aceptante(self):
        col = 'ACEPTANTE'
        if col not in self.df.columns:
            return
        nulos = self.df[col].isna()
        cantidad = nulos.sum()
        if cantidad > 0:
            self.df.loc[nulos, col] = 'SIN ACEPTANTE'
            self._agregar_correccion("ACEPTANTE_NULO", f"Rellenados {cantidad} aceptantes nulos", cantidad)

    def _corregir_monedas_invalidas(self):
        col = 'MONEDA'
        if col not in self.df.columns:
            return
        invalidas = ~self.df[col].isin(MONEDAS_VALIDAS)
        cantidad = invalidas.sum()
        if cantidad > 0:
            self.df.loc[invalidas, col] = 'SOLES'
            self._agregar_correccion("MONEDA_INVÁLIDA", f"Corregidas {cantidad} monedas inválidas", cantidad)

    def _corregir_bancos_invalidos(self):
        col = 'BANCO'
        if col not in self.df.columns:
            return
        invalidos = ~self.df[col].isin(BANCOS_VALIDOS)
        cantidad = invalidos.sum()
        if cantidad > 0:
            self.df.loc[invalidos, col] = 'BBVA'
            self._agregar_correccion("BANCO_INVÁLIDO", f"Corregidos {cantidad} bancos inválidos", cantidad)

    def _corregir_aceptantes_invalidos(self):
        col = 'ACEPTANTE'
        if col not in self.df.columns:
            return
        invalidos = ~self.df[col].isin(ACEPTANTES_VALIDOS)
        cantidad = invalidos.sum()
        if cantidad > 0:
            self.df.loc[invalidos, col] = 'BLACK'
            self._agregar_correccion("ACEPTANTE_INVÁLIDO", f"Corregidos {cantidad} aceptantes inválidos", cantidad)

    def _corregir_productos_invalidos(self):
        col = 'PRODUCTO'
        if col not in self.df.columns:
            return
        invalidos = ~self.df[col].isin(PRODUCTOS_VALIDOS)
        cantidad = invalidos.sum()
        if cantidad > 0:
            self.df.loc[invalidos, col] = 'DEUDA BANCOS'
            self._agregar_correccion("PRODUCTO_INVÁLIDO", f"Corregidos {cantidad} productos inválidos", cantidad)

    def _convertir_tipos_numericos(self):
        for col in ['IMPORTE', 'DOLARES', 'DIAS VENCIDOS']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def _agregar_metadata(self):
        self.df['_limpieza_fecha'] = datetime.now().isoformat()
        self.df['_limpieza_version'] = '1.0'

    def guardar_csv(self, nombre: str = "datos_limpios.csv") -> str:
        DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        ruta = DATA_CLEAN_DIR / nombre
        self.df.to_csv(ruta, index=False)
        return str(ruta)

    def guardar_excel(self, nombre: str = "datos_limpios.xlsx") -> str:
        DATA_CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        ruta = DATA_CLEAN_DIR / nombre
        self.df.to_excel(ruta, index=False)
        return str(ruta)

    def get_resumen_correcciones(self) -> dict:
        return {
            "total_correcciones": len(self.correcciones),
            "correcciones": self.correcciones,
            "filas_originales": None,
            "filas_finales": len(self.df)
        }
