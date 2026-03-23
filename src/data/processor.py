import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class DataProcessor:
    """Clase experta encargada de la limpieza, enriquecimiento e integridad de la data."""

    @staticmethod
    def clean_and_format(df):
        """Aplica las reglas de negocio y limpieza profunda."""
        df = df.copy()
        
        # Filtros de negocio iniciales
        if "CONDICION DEUDA" in df.columns:
            df = df[df["CONDICION DEUDA"] == "PENDIENTE DE PAGO"]
        
        if "IMPORTE" in df.columns:
            df = df[df["IMPORTE"].notna()]

        # Limpieza de Identificadores (Clean Code Fix)
        if "NUMERO UNICO" in df.columns:
            # 1. Identificar nulos o celdas con comentarios de tasas
            mask_vacio = df["NUMERO UNICO"].isna() | df["NUMERO UNICO"].astype(str).str.contains("TASA", case=False)
            
            # 2. Intentar usar Nº LETRA - FACT si existe
            if "Nº LETRA - FACT" in df.columns:
                reemplazo = df.loc[mask_vacio, "Nº LETRA - FACT"].fillna("")
                # Si sigue vacío, generar ID secuencial profesional
                mask_total_vacio = reemplazo == ""
                reemplazo.loc[mask_total_vacio] = "ISD-" + df[mask_vacio][mask_total_vacio].index.astype(str).str.zfill(4)
                df.loc[mask_vacio, "NUMERO UNICO"] = reemplazo
            else:
                df.loc[mask_vacio, "NUMERO UNICO"] = "ID-" + df[mask_vacio].index.astype(str).str.zfill(4)

        # Conversión de Tipos de Datos
        if "Fecha de Vencimiento" in df.columns:
            df["Fecha de Vencimiento"] = pd.to_datetime(df["Fecha de Vencimiento"], errors="coerce")
        
        # Numéricos (Limpia comas y espacios)
        cols_numericas = ["IMPORTE", "DOLARES", "DIAS VENCIDOS"]
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").replace("nan", "0"), errors="coerce").fillna(0)

        # Enriquecimiento Temporal (Feature Engineering)
        if "Fecha de Vencimiento" in df.columns:
            valid_dates = df["Fecha de Vencimiento"].notna()
            df.loc[valid_dates, "MES"] = df.loc[valid_dates, "Fecha de Vencimiento"].dt.to_period("M").astype(str)
            df.loc[valid_dates, "SEMANA"] = df.loc[valid_dates, "Fecha de Vencimiento"].dt.isocalendar().week.astype(str)
            df.loc[valid_dates, "DIA"] = df.loc[valid_dates, "Fecha de Vencimiento"].dt.date
            df.loc[valid_dates, "TRIMESTRE"] = df.loc[valid_dates, "Fecha de Vencimiento"].dt.to_period("Q").astype(str)

        # Rangos de Mora
        if "DIAS VENCIDOS" in df.columns:
            df["RANGO_DIAS"] = pd.cut(
                df["DIAS VENCIDOS"],
                bins=[-np.inf, 0, 30, 60, 90, 180, 365, np.inf],
                labels=["Al dia", "1-30", "31-60", "61-90", "91-180", "181-365", "+365"],
            )

        return df

    @staticmethod
    def calculate_metrics(df, tipo_cambio):
        """Calcula métricas clave consolidadas."""
        soles = df[df["MONEDA"] == "SOLES"]["IMPORTE"].sum()
        dolares = df[df["MONEDA"] == "DOLARES"]["IMPORTE"].sum()
        total_usd = soles / tipo_cambio + dolares
        
        vencidos_df = df[df["DIAS VENCIDOS"] > 0]
        vencidos_count = len(vencidos_df)
        
        return {
            "total_docs": len(df),
            "total_usd": total_usd,
            "soles": soles,
            "dolares": dolares,
            "vencidos": vencidos_count,
            "pct_venc": (vencidos_count / len(df) * 100) if len(df) > 0 else 0,
            "al_dia": len(df[df["DIAS VENCIDOS"] == 0]),
            "por_vencer": len(df[df["DIAS VENCIDOS"] < 0]),
            "riesgo_alto": len(df[df["DIAS VENCIDOS"] > 90]),
            "riesgo_medio": len(df[(df["DIAS VENCIDOS"] > 30) & (df["DIAS VENCIDOS"] <= 90)]),
            "riesgo_bajo": len(df[(df["DIAS VENCIDOS"] > 0) & (df["DIAS VENCIDOS"] <= 30)]),
        }
