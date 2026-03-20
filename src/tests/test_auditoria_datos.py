"""
Auditoria de Datos - Sueno Dorado
Verifica la integridad y precision de los datos del dashboard
"""

import pandas as pd
import os
from datetime import datetime


def auditoria_datos():
    print("=" * 60)
    print("AUDITORIA DE DATOS - SUENO DORADO")
    print("=" * 60)

    # Cargar datos
    excel_path = os.environ.get(
        "DATA_PATH", "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx"
    )
    df = pd.read_excel(excel_path, sheet_name="DATA ORIGINAL", header=2)

    print(f"\n[RESUMEN DE CARGA]")
    print("-" * 40)
    print(f"Total filas leidas: {len(df)}")

    # Filtrar solo pendientes
    df = df[df["CONDICION DEUDA"] == "PENDIENTE DE PAGO"]
    print(f"Despues de filtrar PENDIENTE DE PAGO: {len(df)}")

    # Limpiar datos numericos
    df["IMPORTE"] = pd.to_numeric(
        df["IMPORTE"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DOLARES"] = pd.to_numeric(
        df["DOLARES"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DIAS VENCIDOS"] = pd.to_numeric(
        df["DIAS VENCIDOS"].astype(str).str.replace(",", ""), errors="coerce"
    )

    print(f"\n[VERIFICACION DE COLUMNAS]")
    print("-" * 40)
    for col in [
        "NUMERO UNICO",
        "GIRADOR",
        "MONEDA",
        "BANCO",
        "IMPORTE",
        "DOLARES",
        "DIAS VENCIDOS",
    ]:
        nulos = df[col].isna().sum()
        print(f"{col}: {nulos} nulos")

    # Analisis por moneda
    print(f"\n[ANALISIS POR MONEDA]")
    print("-" * 40)

    soles = df[df["MONEDA"] == "SOLES"]
    dolares = df[df["MONEDA"] == "DOLARES"]

    print(f"SOLES: {len(soles)} registros")
    print(f"  - IMPORTE total: S/. {soles['IMPORTE'].sum():,.2f}")
    print(f"  - DOLARES: $ {soles['DOLARES'].sum():,.2f}")

    print(f"\nDOLARES: {len(dolares)} registros")
    print(f"  - IMPORTE total: S/. {dolares['IMPORTE'].sum():,.2f}")
    print(f"  - DOLARES: $ {dolares['DOLARES'].sum():,.2f}")

    # Totales
    total_importe = df["IMPORTE"].sum()
    total_dolares = df["DOLARES"].sum()

    print(f"\n[TOTALES]")
    print("-" * 40)
    print(f"IMPORTE total: S/. {total_importe:,.2f}")
    print(f"DOLARES total: $ {total_dolares:,.2f}")

    # Verificar si DOLARES para SOLES es correcto (IMPORTE / 3.45)
    tipo_cambio = 3.45
    print(f"\n[VERIFICACION TIPO DE CAMBIO ({tipo_cambio})]")
    print("-" * 40)

    soles_check = soles.copy()
    soles_check["DOLARES_CALC"] = soles_check["IMPORTE"] / tipo_cambio
    soles_check["DOLARES_ORIG"] = soles_check["DOLARES"]
    soles_check["DIFERENCIA"] = abs(
        soles_check["DOLARES_CALC"] - soles_check["DOLARES_ORIG"]
    )

    errores_tc = soles_check[soles_check["DIFERENCIA"] > 0.01]
    if len(errores_tc) > 0:
        print(f"ERROR: {len(errores_tc)} registros con diferencia > 0.01")
        print(
            errores_tc[
                ["GIRADOR", "IMPORTE", "DOLARES_ORIG", "DOLARES_CALC", "DIFERENCIA"]
            ].head()
        )
    else:
        print("OK: Todos los registros en SOLES tienen DOLARES correcto")

    # Clasificacion vencidos
    print(f"\n[CLASIFICACION POR VENCIMIENTO]")
    print("-" * 40)

    vencidos = df[df["DIAS VENCIDOS"] > 0]
    al_dia = df[df["DIAS VENCIDOS"] <= 0]

    print(
        f"Vencidos (>0 dias): {len(vencidos)} registros - S/. {vencidos['IMPORTE'].sum():,.2f}"
    )
    print(
        f"Al dia (<=0 dias): {len(al_dia)} registros - S/. {al_dia['IMPORTE'].sum():,.2f}"
    )

    # Por banco
    print(f"\n[DISTRIBUCION POR BANCO]")
    print("-" * 40)
    banco = df.groupby("BANCO")["IMPORTE"].sum().sort_values(ascending=False)
    for b, v in banco.items():
        print(f"  {b}: S/. {v:,.2f}")

    # Por moneda
    print(f"\n[DISTRIBUCION POR MONEDA]")
    print("-" * 40)
    moneda = df.groupby("MONEDA")["IMPORTE"].sum()
    for m, v in moneda.items():
        print(f"  {m}: S/. {v:,.2f}")

    # Por producto
    print(f"\n[DISTRIBUCION POR PRODUCTO]")
    print("-" * 40)
    producto = df.groupby("PRODUCTO")["IMPORTE"].sum().sort_values(ascending=False)
    for p, v in producto.items():
        print(f"  {p}: S/. {v:,.2f}")

    print(f"\n[AUDITORIA COMPLETADA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 60)


if __name__ == "__main__":
    auditoria_datos()
