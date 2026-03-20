"""
ANALISIS EXHAUSTIVO DE CALCULOS - SUENO DORADO
=================================================

Este script verifica y documenta TODAS las formulas y calculos
usados en el dashboard para garantizar precision de datos.
"""

import pandas as pd
import os
from datetime import datetime


def analisis_calculos():
    print("=" * 70)
    print("ANALISIS EXHAUSTIVO DE CALCULOS - SUENO DORADO")
    print("=" * 70)

    # Cargar datos
    excel_path = os.environ.get(
        "DATA_PATH", "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx"
    )
    df = pd.read_excel(excel_path, sheet_name="DATA ORIGINAL", header=2)

    print(f"\n[1] DATOS CARGADOS")
    print("-" * 50)
    print(f"Total filas: {len(df)}")
    print(f"Columnas: {list(df.columns)}")

    # Filtrar solo pendientes
    df = df[df["CONDICION DEUDA"] == "PENDIENTE DE PAGO"].copy()
    print(f"Despues de filtrar PENDIENTE DE PAGO: {len(df)}")

    # Limpiar datos
    df["IMPORTE"] = pd.to_numeric(
        df["IMPORTE"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DOLARES"] = pd.to_numeric(
        df["DOLARES"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DIAS VENCIDOS"] = pd.to_numeric(
        df["DIAS VENCIDOS"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["Fecha de Vencimiento"] = pd.to_datetime(
        df["Fecha de Vencimiento"], errors="coerce"
    )

    tipo_cambio = 3.45

    print("\n" + "=" * 70)
    print("[2] ANALISIS DE MONEDAS Y CONVERSION")
    print("-" * 50)

    # Analisis por moneda
    soles = df[df["MONEDA"] == "SOLES"].copy()
    dolares = df[df["MONEDA"] == "DOLARES"].copy()

    print(f"\n[2.1] Documentos en SOLES:")
    print(f"  Cantidad: {len(soles)}")
    print(f"  IMPORTE (S/.): {soles['IMPORTE'].sum():,.2f}")
    print(
        f"  DOLARES (calculado = IMPORTE / {tipo_cambio}): {soles['IMPORTE'].sum() / tipo_cambio:,.2f}"
    )
    print(f"  DOLARES (en data): {soles['DOLARES'].sum():,.2f}")

    print(f"\n[2.2] Documentos en DOLARES:")
    print(f"  Cantidad: {len(dolares)}")
    print(f"  IMPORTE (ya es USD): {dolares['IMPORTE'].sum():,.2f}")
    print(f"  DOLARES (igual a IMPORTE): {dolares['DOLARES'].sum():,.2f}")

    # Formula CORRECTA para conversion a USD
    df["IMPORTE_USD_CORRECTO"] = df.apply(
        lambda x: (
            x["IMPORTE"] / tipo_cambio if x["MONEDA"] == "SOLES" else x["IMPORTE"]
        ),
        axis=1,
    )

    print(f"\n[2.3] TOTAL CARTERA EQUIVALENTE USD:")
    print(f"  IMPORTE_USD = SUMA(IMPORTE_SOLES/{tipo_cambio} + IMPORTE_DOLARES)")
    print(
        f"  = {soles['IMPORTE'].sum():,.2f} / {tipo_cambio} + {dolares['IMPORTE'].sum():,.2f}"
    )
    print(
        f"  = {soles['IMPORTE'].sum() / tipo_cambio:,.2f} + {dolares['IMPORTE'].sum():,.2f}"
    )
    print(f"  = {df['IMPORTE_USD_CORRECTO'].sum():,.2f}")

    print("\n" + "=" * 70)
    print("[3] CLASIFICACION DE DOCUMENTOS POR VENCIMIENTO")
    print("-" * 50)

    # Clasificacion CORRECTA
    vencidos = df[df["DIAS VENCIDOS"] > 0]  # Ya vencio
    al_dia = df[df["DIAS VENCIDOS"] == 0]  # Vence hoy
    por_vencer = df[df["DIAS VENCIDOS"] < 0]  # Todavia no vence

    print(f"\n[3.1] Documentos VENCIDOS (DIAS VENCIDOS > 0):")
    print(f"  Cantidad: {len(vencidos)}")
    print(f"  Monto Total: S/. {vencidos['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[df['DIAS VENCIDOS'] > 0]")

    print(f"\n[3.2] Documentos AL DIA (DIAS VENCIDOS == 0):")
    print(f"  Cantidad: {len(al_dia)}")
    print(f"  Monto Total: S/. {al_dia['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[df['DIAS VENCIDOS'] == 0]")

    print(f"\n[3.3] Documentos POR VENCER (DIAS VENCIDOS < 0):")
    print(f"  Cantidad: {len(por_vencer)}")
    print(f"  Monto Total: S/. {por_vencer['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[df['DIAS VENCIDOS'] < 0]")

    print(f"\n[3.4] VERIFICACION:")
    print(
        f"  Vencidos + Al Dia + Por Vencer = {len(vencidos) + len(al_dia) + len(por_vencer)}"
    )
    print(f"  Total Documentos = {len(df)}")
    print(f"  CUADRA: {len(vencidos) + len(al_dia) + len(por_vencer) == len(df)}")

    print("\n" + "=" * 70)
    print("[4] CLASIFICACION DE RIESGO")
    print("-" * 50)

    riesgo_alto = df[df["DIAS VENCIDOS"] > 90]
    riesgo_medio = df[(df["DIAS VENCIDOS"] > 30) & (df["DIAS VENCIDOS"] <= 90)]
    riesgo_bajo = df[(df["DIAS VENCIDOS"] > 0) & (df["DIAS VENCIDOS"] <= 30)]

    print(f"\n[4.1] RIESGO ALTO (>90 dias):")
    print(f"  Cantidad: {len(riesgo_alto)}")
    print(f"  Monto: S/. {riesgo_alto['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[df['DIAS VENCIDOS'] > 90]")

    print(f"\n[4.2] RIESGO MEDIO (31-90 dias):")
    print(f"  Cantidad: {len(riesgo_medio)}")
    print(f"  Monto: S/. {riesgo_medio['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[(df['DIAS VENCIDOS'] > 30) & (df['DIAS VENCIDOS'] <= 90)]")

    print(f"\n[4.3] RIESGO BAJO (1-30 dias):")
    print(f"  Cantidad: {len(riesgo_bajo)}")
    print(f"  Monto: S/. {riesgo_bajo['IMPORTE'].sum():,.2f}")
    print(f"  Formula: df[(df['DIAS VENCIDOS'] > 0) & (df['DIAS VENCIDOS'] <= 30)]")

    print(f"\n[4.4] VERIFICACION:")
    print(
        f"  Total vencidos = {len(riesgo_alto) + len(riesgo_medio) + len(riesgo_bajo)}"
    )
    print(f"  Vencidos total = {len(vencidos)}")
    print(
        f"  CUADRA: {len(riesgo_alto) + len(riesgo_medio) + len(riesgo_bajo) == len(vencidos)}"
    )

    print("\n" + "=" * 70)
    print("[5] ANALISIS POR BANCO")
    print("-" * 50)

    por_banco = df.groupby("BANCO").agg(
        {"NUMERO UNICO": "count", "IMPORTE": "sum", "DIAS VENCIDOS": ["mean", "max"]}
    )
    por_banco.columns = ["Docs", "Monto_Soles", "Prom_Dias", "Max_Dias"]
    por_banco = por_banco.sort_values("Monto_Soles", ascending=False)

    print("\nBanco              | Docs | Monto S/.      | Prom Dias | Max Dias")
    print("-" * 70)
    for idx, row in por_banco.iterrows():
        print(
            f"{str(idx):<18} | {row['Docs']:>4} | {row['Monto_Soles']:>14,.2f} | {row['Prom_Dias']:>9.1f} | {row['Max_Dias']:>9.0f}"
        )

    print(f"\n[5.1] TOTALES:")
    print(f"  Total Documentos: {por_banco['Docs'].sum()}")
    print(f"  Total Monto: S/. {por_banco['Monto_Soles'].sum():,.2f}")

    print("\n" + "=" * 70)
    print("[6] ANALISIS POR GIRADOR")
    print("-" * 50)

    por_girador = df.groupby("GIRADOR").agg(
        {"NUMERO UNICO": "count", "IMPORTE": "sum", "DIAS VENCIDOS": ["mean", "max"]}
    )
    por_girador.columns = ["Docs", "Monto_Soles", "Prom_Dias", "Max_Dias"]
    por_girador["Vencidos"] = (
        df[df["DIAS VENCIDOS"] > 0]
        .groupby("GIRADOR")
        .size()
        .reindex(por_girador.index)
        .fillna(0)
    )
    por_girador["Porcentaje"] = (
        por_girador["Monto_Soles"] / por_girador["Monto_Soles"].sum() * 100
    )
    por_girador = por_girador.sort_values("Monto_Soles", ascending=False)

    print("\nTop 10 Giradores:")
    print("-" * 90)
    print("Girador           | Docs | Monto S/.      | Venc | Prom Dias | %")
    print("-" * 90)
    for idx, row in por_girador.head(10).iterrows():
        nombre = str(idx)[:17] if len(str(idx)) > 17 else str(idx)
        print(
            f"{nombre:<17} | {row['Docs']:>4} | {row['Monto_Soles']:>14,.2f} | {int(row['Vencidos']):>4} | {row['Prom_Dias']:>9.1f} | {row['Porcentaje']:>5.1f}%"
        )

    print(f"\n[6.1] CONCENTRACION:")
    top3 = por_girador.head(3)["Monto_Soles"].sum()
    total = por_girador["Monto_Soles"].sum()
    print(f"  Top 3 giradores: S/. {top3:,.2f}")
    print(f"  Porcentaje del total: {top3 / total * 100:.1f}%")

    print("\n" + "=" * 70)
    print("[7] RESUMEN EJECUTIVO FINAL")
    print("-" * 50)

    print(f"""
    [RESUMEN DE METRICAS]
    =====================
    
    1. TOTAL DOCUMENTOS: {len(df)}
    
    2. CARTERA TOTAL (USD): ${df["IMPORTE_USD_CORRECTO"].sum():,.2f}
       - SOLES: S/. {soles["IMPORTE"].sum():,.2f} / {tipo_cambio} = ${soles["IMPORTE"].sum() / tipo_cambio:,.2f}
       - DOLARES: ${dolares["IMPORTE"].sum():,.2f}
       - TOTAL USD: ${df["IMPORTE_USD_CORRECTO"].sum():,.2f}
    
    3. CLASIFICACION:
       - VENCIDOS: {len(vencidos)} docs - S/. {vencidos["IMPORTE"].sum():,.2f}
       - AL DIA: {len(al_dia)} docs - S/. {al_dia["IMPORTE"].sum():,.2f}
       - POR VENCER: {len(por_vencer)} docs - S/. {por_vencer["IMPORTE"].sum():,.2f}
       - TOTAL: {len(vencidos) + len(al_dia) + len(por_vencer)} docs - S/. {df["IMPORTE"].sum():,.2f}
    
    4. RIESGOS (solo vencidos):
       - ALTO (>90d): {len(riesgo_alto)} - S/. {riesgo_alto["IMPORTE"].sum():,.2f}
       - MEDIO (31-90d): {len(riesgo_medio)} - S/. {riesgo_medio["IMPORTE"].sum():,.2f}
       - BAJO (1-30d): {len(riesgo_bajo)} - S/. {riesgo_bajo["IMPORTE"].sum():,.2f}
    
    5. DISTRIBUCION:
       - BCP: S/. {por_banco.loc["BCP", "Monto_Soles"]:,.2f} ({por_banco.loc["BCP", "Monto_Soles"] / total * 100:.1f}%)
       - BBVA: S/. {por_banco.loc["BBVA", "Monto_Soles"]:,.2f} ({por_banco.loc["BBVA", "Monto_Soles"] / total * 100:.1f}%)
       - BLACK: S/. {por_banco.loc["BLACK", "Monto_Soles"]:,.2f} ({por_banco.loc["BLACK", "Monto_Soles"] / total * 100:.1f}%)
    """)

    print("=" * 70)
    print(f"AUDITORIA COMPLETADA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    analisis_calculos()
