"""Módulo de carga de datos desde Excel."""
import pandas as pd
from pathlib import Path
from config.settings import EXCEL_FILE, EXCEL_SHEET, SKIP_ROWS, BASE_DIR


class DataLoader:
    """Carga datos desde archivo Excel con configuración centralizada."""
    
    def __init__(self, file_path: str = None, sheet: str = None, skip_rows: int = None):
        self.file_path = file_path or str(BASE_DIR / EXCEL_FILE)
        self.sheet = sheet or EXCEL_SHEET
        self.skip_rows = skip_rows if skip_rows is not None else SKIP_ROWS
    
    def cargar(self) -> pd.DataFrame:
        """Carga el archivo Excel y retorna DataFrame."""
        df = pd.read_excel(self.file_path, sheet_name=self.sheet, skiprows=self.skip_rows)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    
    def cargar_info_basica(self) -> dict:
        """Retorna información básica del dataset."""
        df = self.cargar()
        return {
            "archivo": self.file_path,
            "hoja": self.sheet,
            "columnas": list(df.columns),
            "filas": len(df),
            "memoria_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
        }
