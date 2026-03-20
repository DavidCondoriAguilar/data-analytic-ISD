"""
ANALISIS EXHAUSTIVO - TODOS LOS ESCENARIOS Y FILTROS
=====================================================
Este script prueba TODAS las combinaciones de filtros para verificar
que los calculos sean correctos y cuadren.
"""

import pandas as pd
import os
from datetime import datetime, timedelta


def analisis_exhaustivo():
    print("=" * 80)
    print("ANALISIS EXHAUSTIVO - TODOS LOS FILTROS Y ESCENARIOS")
    print("=" * 80)

    # Cargar datos
    excel_path = "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx"
    df = pd.read_excel(excel_path, sheet_name="DATA ORIGINAL", header=2)

    print(f"\n[0] DATOS BASE")
    print("-" * 50)
    print(f"Total filas leidas: {len(df)}")

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

    # Filtrar solo pendientes y sin filas vacías
    df_pendientes = df[
        (df["CONDICION DEUDA"] == "PENDIENTE DE PAGO") & (df["IMPORTE"].notna())
    ].copy()

    # Llenar NUMERO UNICO desde Nº LETRA - FACT si está vacío
    if "NUMERO UNICO" in df_pendientes.columns:
        mask = df_pendientes["NUMERO UNICO"].isna()
        df_pendientes.loc[mask, "NUMERO UNICO"] = df_pendientes.loc[
            mask, "Nº LETRA - FACT"
        ]
    print(f"Despues de filtrar PENDIENTE DE PAGO: {len(df_pendientes)}")

    tipo_cambio = 3.45
    hoy = datetime.now().date()

    # Agregar columna USD
    df_pendientes["IMPORTE_USD"] = df_pendientes.apply(
        lambda x: (
            x["IMPORTE"] / tipo_cambio if x["MONEDA"] == "SOLES" else x["IMPORTE"]
        ),
        axis=1,
    )

    print("\n" + "=" * 80)
    print("[1] ANALISIS DE VALORES UNICOS POR COLUMNA")
    print("-" * 50)

    print(f"\n[1.1] BANCOS ({df_pendientes['BANCO'].nunique()} unicos):")
    for banco in sorted(df_pendientes["BANCO"].dropna().unique()):
        count = len(df_pendientes[df_pendientes["BANCO"] == banco])
        monto = df_pendientes[df_pendientes["BANCO"] == banco]["IMPORTE"].sum()
        print(f"  {banco}: {count} docs, S/. {monto:,.2f}")

    print(f"\n[1.2] MONEDAS ({df_pendientes['MONEDA'].nunique()} unicas):")
    for moneda in df_pendientes["MONEDA"].dropna().unique():
        count = len(df_pendientes[df_pendientes["MONEDA"] == moneda])
        monto = df_pendientes[df_pendientes["MONEDA"] == moneda]["IMPORTE"].sum()
        print(f"  {moneda}: {count} docs, S/. {monto:,.2f}")

    print(f"\n[1.3] PRODUCTOS ({df_pendientes['PRODUCTO'].nunique()} unicos):")
    for prod in sorted(df_pendientes["PRODUCTO"].dropna().unique()):
        count = len(df_pendientes[df_pendientes["PRODUCTO"] == prod])
        monto = df_pendientes[df_pendientes["PRODUCTO"] == prod]["IMPORTE"].sum()
        print(f"  {prod}: {count} docs, S/. {monto:,.2f}")

    print(f"\n[1.4] GIRADORES ({df_pendientes['GIRADOR'].nunique()} unicos):")
    for gir in sorted(df_pendientes["GIRADOR"].dropna().unique())[:10]:
        count = len(df_pendientes[df_pendientes["GIRADOR"] == gir])
        monto = df_pendientes[df_pendientes["GIRADOR"] == gir]["IMPORTE"].sum()
        print(f"  {gir}: {count} docs, S/. {monto:,.2f}")
    print(f"  ... y {df_pendientes['GIRADOR'].nunique() - 10} mas")

    print("\n" + "=" * 80)
    print("[2] ESCENARIO 1: SIN NINGUN FILTRO (TODOS LOS DATOS)")
    print("-" * 50)

    df_f = df_pendientes.copy()

    soles_t = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares_t = df_f[df_f["MONEDA"] == "DOLARES"]["DOLARES"].sum()
    total_usd_t = df_f["IMPORTE_USD"].sum()

    vencidos_t = len(df_f[df_f["DIAS VENCIDOS"] > 0])
    al_dia_t = len(df_f[df_f["DIAS VENCIDOS"] == 0])
    por_vencer_t = len(df_f[df_f["DIAS VENCIDOS"] < 0])

    print(f"Total Documentos: {len(df_f)}")
    print(f"Cartera Total USD: ${total_usd_t:,.2f}")
    print(f"Cartera Soles: S/. {soles_t:,.2f}")
    print(f"Cartera Dolares: ${dolares_t:,.2f}")
    print(f"")
    print(f"VENCIDOS (>0 dias): {vencidos_t} docs")
    print(f"AL DIA (==0 dias): {al_dia_t} docs")
    print(f"POR VENCER (<0 dias): {por_vencer_t} docs")
    print(f"TOTAL: {vencidos_t + al_dia_t + por_vencer_t}")
    print(f"")
    print(
        f"VERIFICACION: {vencidos_t + al_dia_t + por_vencer_t} == {len(df_f)} ? {vencidos_t + al_dia_t + por_vencer_t == len(df_f)}"
    )

    print("\n" + "=" * 80)
    print("[3] ESCENARIO 2: FILTRO POR BANCO - BCP")
    print("-" * 50)

    df_f = df_pendientes[df_pendientes["BANCO"] == "BCP"].copy()

    soles_t = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares_t = df_f[df_f["MONEDA"] == "DOLARES"]["DOLARES"].sum()
    total_usd_t = df_f["IMPORTE_USD"].sum()

    vencidos_t = len(df_f[df_f["DIAS VENCIDOS"] > 0])
    al_dia_t = len(df_f[df_f["DIAS VENCIDOS"] == 0])
    por_vencer_t = len(df_f[df_f["DIAS VENCIDOS"] < 0])

    print(f"Total Documentos: {len(df_f)}")
    print(f"Cartera Total USD: ${total_usd_t:,.2f}")
    print(f"VENCIDOS: {vencidos_t}, AL DIA: {al_dia_t}, POR VENCER: {por_vencer_t}")

    print("\n" + "=" * 80)
    print("[4] ESCENARIO 3: FILTRO POR MONEDA - DOLARES")
    print("-" * 50)

    df_f = df_pendientes[df_pendientes["MONEDA"] == "DOLARES"].copy()

    soles_t = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares_t = df_f[df_f["MONEDA"] == "DOLARES"]["DOLARES"].sum()
    total_usd_t = df_f["IMPORTE_USD"].sum()

    vencidos_t = len(df_f[df_f["DIAS VENCIDOS"] > 0])
    al_dia_t = len(df_f[df_f["DIAS VENCIDOS"] == 0])
    por_vencer_t = len(df_f[df_f["DIAS VENCIDOS"] < 0])

    print(f"Total Documentos: {len(df_f)}")
    print(f"Cartera Total USD: ${total_usd_t:,.2f}")
    print(f"VENCIDOS: {vencidos_t}, AL DIA: {al_dia_t}, POR VENCER: {por_vencer_t}")

    print("\n" + "=" * 80)
    print("[5] ESCENARIO 4: SOLO VENCIDOS (filtro rapido)")
    print("-" * 50)

    df_f = df_pendientes[df_pendientes["DIAS VENCIDOS"] > 0].copy()

    soles_t = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares_t = df_f[df_f["MONEDA"] == "DOLARES"]["DOLARES"].sum()
    total_usd_t = df_f["IMPORTE_USD"].sum()

    riesgo_alto = len(df_f[df_f["DIAS VENCIDOS"] > 90])
    riesgo_medio = len(
        df_f[(df_f["DIAS VENCIDOS"] > 30) & (df_f["DIAS VENCIDOS"] <= 90)]
    )
    riesgo_bajo = len(df_f[(df_f["DIAS VENCIDOS"] > 0) & (df_f["DIAS VENCIDOS"] <= 30)])

    print(f"Total Documentos Vencidos: {len(df_f)}")
    print(f"Cartera Total USD: ${total_usd_t:,.2f}")
    print(f"Cartera Soles: S/. {soles_t:,.2f}")
    print(f"Cartera Dolares: ${dolares_t:,.2f}")
    print(f"")
    print(f"RIESGO ALTO (>90d): {riesgo_alto}")
    print(f"RIESGO MEDIO (31-90d): {riesgo_medio}")
    print(f"RIESGO BAJO (1-30d): {riesgo_bajo}")
    print(f"TOTAL RIESGOS: {riesgo_alto + riesgo_medio + riesgo_bajo}")

    print("\n" + "=" * 80)
    print("[6] ESCENARIO 5: FILTRO POR PERIODO - 1 MES")
    print("-" * 50)

    fecha_ini = hoy - timedelta(days=30)
    fecha_fin_calc = hoy

    df_f = df_pendientes[
        (df_pendientes["Fecha de Vencimiento"] >= pd.to_datetime(fecha_ini))
        & (df_pendientes["Fecha de Vencimiento"] <= pd.to_datetime(fecha_fin_calc))
    ].copy()

    soles_t = df_f[df_f["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares_t = df_f[df_f["MONEDA"] == "DOLARES"]["DOLARES"].sum()
    total_usd_t = df_f["IMPORTE_USD"].sum()

    vencidos_t = len(df_f[df_f["DIAS VENCIDOS"] > 0])
    al_dia_t = len(df_f[df_f["DIAS VENCIDOS"] == 0])
    por_vencer_t = len(df_f[df_f["DIAS VENCIDOS"] < 0])

    print(f"Fecha ini: {fecha_ini}, Fecha fin: {fecha_fin_calc}")
    print(f"Total Documentos: {len(df_f)}")
    print(f"Cartera Total USD: ${total_usd_t:,.2f}")
    print(f"VENCIDOS: {vencidos_t}, AL DIA: {al_dia_t}, POR VENCER: {por_vencer_t}")

    print("\n" + "=" * 80)
    print("[7] VERIFICACION DE CALCULOS")
    print("-" * 50)

    # Verificar que IMPORTE_USD sea correcto
    print("\n[7.1] Verificando IMPORTE_USD:")
    for idx, row in df_pendientes.head(5).iterrows():
        importe = row["IMPORTE"]
        moneda = row["MONEDA"]
        dolares_orig = row["DOLARES"]
        importe_usd_calc = row["IMPORTE_USD"]

        if moneda == "SOLES":
            esperado = importe / tipo_cambio
        else:
            esperado = importe

        print(
            f"  {moneda}: IMPORTE={importe:,.2f}, DOLARES_orig={dolares_orig:,.2f}, USD_calc={importe_usd_calc:,.2f}, esperado={esperado:,.2f}, cuadra={abs(importe_usd_calc - esperado) < 0.01}"
        )

    print("\n[7.2] Verificando clasificacion vencidos:")
    total = len(df_pendientes)
    vencidos = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] > 0])
    al_dia = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] == 0])
    por_vencer = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] < 0])

    print(f"  Total: {total}")
    print(f"  Vencidos (>0): {vencidos}")
    print(f"  Al dia (==0): {al_dia}")
    print(f"  Por vencer (<0): {por_vencer}")
    print(f"  Suma: {vencidos + al_dia + por_vencer}")
    print(f"  Cuadra: {vencidos + al_dia + por_vencer == total}")

    print("\n" + "=" * 80)
    print("[8] DATOS PARA COMPARAR CON EXCEL")
    print("-" * 50)

    print(f"\nTOTAL GENERAL:")
    print(f"  Total Docs: {len(df_pendientes)}")
    print(f"  Total IMPORTE: S/. {df_pendientes['IMPORTE'].sum():,.2f}")
    print(f"  Total DOLARES: ${df_pendientes['DOLARES'].sum():,.2f}")
    print(f"  Total IMPORTE_USD: ${df_pendientes['IMPORTE_USD'].sum():,.2f}")

    print(f"\nPOR MONEDA:")
    for m in df_pendientes["MONEDA"].unique():
        df_m = df_pendientes[df_pendientes["MONEDA"] == m]
        print(
            f"  {m}: {len(df_m)} docs, S/. {df_m['IMPORTE'].sum():,.2f}, USD: ${df_m['IMPORTE_USD'].sum():,.2f}"
        )

    print(f"\nPOR VENCIMIENTO:")
    v = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] > 0])
    a = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] == 0])
    p = len(df_pendientes[df_pendientes["DIAS VENCIDOS"] < 0])
    print(
        f"  Vencidos (>0): {v} docs, S/. {df_pendientes[df_pendientes['DIAS VENCIDOS'] > 0]['IMPORTE'].sum():,.2f}"
    )
    print(
        f"  Al dia (==0): {a} docs, S/. {df_pendientes[df_pendientes['DIAS VENCIDOS'] == 0]['IMPORTE'].sum():,.2f}"
    )
    print(
        f"  Por vencer (<0): {p} docs, S/. {df_pendientes[df_pendientes['DIAS VENCIDOS'] < 0]['IMPORTE'].sum():,.2f}"
    )

    print("\n" + "=" * 80)
    print(f"ANALISIS COMPLETADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    analisis_exhaustivo()
