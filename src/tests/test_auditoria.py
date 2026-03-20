"""
AUDITORIA EXHAUSTIVA DE DATA - ISD
Nivel Senior - Garantia de calidad al 100%
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime
from src.data.cleaner import DataCleaner
from src.data.validator import DataValidator


def cargar_data():
    """Carga y procesa data"""
    df_raw = pd.read_excel(
        "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx",
        sheet_name="DATA ORIGINAL",
        header=2,
    )
    cleaner = DataCleaner(df_raw)
    df_clean, _ = cleaner.limpiar_todo()
    return df_clean


def test_conversion_moneda():
    """TEST 1: Verifica conversion SOLES -> USD"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")
    df["DOLARES"] = pd.to_numeric(df["DOLARES"], errors="coerce")

    soles = df[df["MONEDA"] == "SOLES"].copy()
    errores = 0

    for _, row in soles[soles["DOLARES"].notna()].iterrows():
        esperado = row["IMPORTE"] / 3.45
        diferencia = abs(row["DOLARES"] - esperado)
        if diferencia > 0.02:
            errores += 1

    return {
        "test": "Conversion Moneda SOLES->USD",
        "total": len(soles),
        "errores": errores,
        "pasado": errores == 0,
    }


def test_fechas_validas():
    """TEST 2: Verifica fechas en rango"""
    df = cargar_data()
    df["Fecha de Vencimiento"] = pd.to_datetime(
        df["Fecha de Vencimiento"], errors="coerce"
    )

    nulas = df["Fecha de Vencimiento"].isna().sum()
    df["ANIO"] = df["Fecha de Vencimiento"].dt.year
    fuera_rango = len(df[(df["ANIO"] < 2024) | (df["ANIO"] > 2028)])

    return {
        "test": "Fechas Validas",
        "nulas": nulas,
        "fuera_rango": fuera_rango,
        "pasado": nulas == 0 and fuera_rango == 0,
    }


def test_entidades_completas():
    """TEST 3: Verifica entidades sin nulos"""
    df = cargar_data()

    giradores_nulos = df["GIRADOR"].isna().sum()
    aceptantes_nulos = df["ACEPTANTE"].isna().sum()
    bancos_nulos = df["BANCO"].isna().sum()

    return {
        "test": "Entidades Completas",
        "giradores_nulos": giradores_nulos,
        "aceptantes_nulos": aceptantes_nulos,
        "bancos_nulos": bancos_nulos,
        "pasado": giradores_nulos == 0 and aceptantes_nulos == 0,
    }


def test_montos_positivos():
    """TEST 4: Verifica montos positivos"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")

    negativos = len(df[df["IMPORTE"] < 0])
    ceros = len(df[df["IMPORTE"] == 0])

    return {
        "test": "Montos Positivos",
        "negativos": negativos,
        "ceros": ceros,
        "pasado": negativos == 0 and ceros == 0,
    }


def test_tipo_cambio_consistente():
    """TEST 5: Verifica tipo de cambio consistente"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")
    df["DOLARES"] = pd.to_numeric(df["DOLARES"], errors="coerce")

    soles = df[(df["MONEDA"] == "SOLES") & (df["DOLARES"] > 0)]
    tipos_cambio = []

    for _, row in soles.iterrows():
        if row["DOLARES"] > 0:
            tc = row["IMPORTE"] / row["DOLARES"]
            tipos_cambio.append(tc)

    if tipos_cambio:
        promedio = sum(tipos_cambio) / len(tipos_cambio)
        tc_fuera_rango = len([t for t in tipos_cambio if t < 3.40 or t > 3.50])
        return {
            "test": "Tipo de Cambio Consistente",
            "promedio": promedio,
            "fuera_rango": tc_fuera_rango,
            "pasado": tc_fuera_rango == 0,
        }
    return {"test": "Tipo de Cambio", "promedio": 0, "fuera_rango": 0, "pasado": True}


def test_analisis_vencimiento():
    """ANALISIS: Estado de vencimiento"""
    df = cargar_data()
    df["DIAS VENCIDOS"] = pd.to_numeric(df["DIAS VENCIDOS"], errors="coerce")

    vencidos = len(df[df["DIAS VENCIDOS"] > 0])
    al_dia = len(df[df["DIAS VENCIDOS"] == 0])
    por_vencer = len(df[df["DIAS VENCIDOS"] < 0])

    return {
        "vencidos": vencidos,
        "al_dia": al_dia,
        "por_vencer": por_vencer,
        "total": len(df),
    }


def test_resumen_montos():
    """ANALISIS: Resumen de montos"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")
    df["DOLARES"] = pd.to_numeric(df["DOLARES"], errors="coerce")

    soles = df[df["MONEDA"] == "SOLES"]
    dolares = df[df["MONEDA"] == "DOLARES"]

    return {
        "total_documentos": len(df),
        "total_soles": float(soles["IMPORTE"].sum()),
        "total_dolares": float(dolares["DOLARES"].sum()),
        "promedio_soles": float(soles["IMPORTE"].mean()),
        "maximo_soles": float(soles["IMPORTE"].max()),
    }


def test_distribucion_empresas():
    """ANALISIS: Distribucion por empresa"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")

    por_emp = (
        df.groupby("ACEPTANTE")
        .agg({"IMPORTE": "sum", "Nº LETRA - FACT": "count"})
        .sort_values("IMPORTE", ascending=False)
    )

    return por_emp.to_dict("index")


def test_distribucion_productos():
    """ANALISIS: Distribucion por producto"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")

    por_prod = df.groupby("PRODUCTO")["IMPORTE"].sum().sort_values(ascending=False)

    return por_prod.to_dict()


def test_riesgo_concentracion():
    """ANALISIS: Riesgo de concentracion"""
    df = cargar_data()
    df["IMPORTE"] = pd.to_numeric(df["IMPORTE"], errors="coerce")

    por_emp = df.groupby("ACEPTANTE")["IMPORTE"].sum()
    total = por_emp.sum()

    concentracion = {}
    for emp, monto in por_emp.items():
        concentracion[emp] = {
            "monto": float(monto),
            "porcentaje": float(monto / total * 100) if total > 0 else 0,
        }

    # Identificar concentracion > 40%
    alto_riesgo = {k: v for k, v in concentracion.items() if v["porcentaje"] > 40}

    return {
        "distribucion": concentracion,
        "alto_riesgo": alto_riesgo,
        "total_empresas": len(concentracion),
    }


def run_auditoria_completa():
    """Ejecuta auditoria completa"""
    print("=" * 70)
    print("AUDITORIA EXHAUSTIVA DE DATA - ISD")
    print("=" * 70)

    print()
    print("[1] TEST: CONVERSION MONEDA")
    result = test_conversion_moneda()
    print(f"    Documentos SOLES: {result['total']}")
    print(f"    Errores de conversion: {result['errores']}")
    print(f"    ESTADO: {'PASADO' if result['pasado'] else 'FALLO'}")

    print()
    print("[2] TEST: FECHAS VALIDAS")
    result = test_fechas_validas()
    print(f"    Fechas nulas: {result['nulas']}")
    print(f"    Fuera de rango: {result['fuera_rango']}")
    print(f"    ESTADO: {'PASADO' if result['pasado'] else 'FALLO'}")

    print()
    print("[3] TEST: ENTIDADES COMPLETAS")
    result = test_entidades_completas()
    print(f"    Giradores nulos: {result['giradores_nulos']}")
    print(f"    Aceptantes nulos: {result['aceptantes_nulos']}")
    print(f"    ESTADO: {'PASADO' if result['pasado'] else 'FALLO'}")

    print()
    print("[4] TEST: MONTOS POSITIVOS")
    result = test_montos_positivos()
    print(f"    Negativos: {result['negativos']}")
    print(f"    Ceros: {result['ceros']}")
    print(f"    ESTADO: {'PASADO' if result['pasado'] else 'FALLO'}")

    print()
    print("[5] TEST: TIPO DE CAMBIO")
    result = test_tipo_cambio_consistente()
    print(f"    TC Promedio: {result['promedio']:.4f}")
    print(f"    Fuera de rango: {result['fuera_rango']}")
    print(f"    ESTADO: {'PASADO' if result['pasado'] else 'FALLO'}")

    print()
    print("-" * 70)
    print("ANALISIS DE VENCIMIENTO")
    print("-" * 70)
    result = test_analisis_vencimiento()
    print(f"    Total documentos: {result['total']}")
    print(f"    Vencidos (>0 dias): {result['vencidos']}")
    print(f"    Al dia (=0 dias): {result['al_dia']}")
    print(f"    Por vencer (<0 dias): {result['por_vencer']}")

    print()
    print("-" * 70)
    print("RESUMEN DE MONTOS")
    print("-" * 70)
    result = test_resumen_montos()
    print(f"    Total documentos: {result['total_documentos']}")
    print(f"    Total en SOLES: S/. {result['total_soles']:,.2f}")
    print(f"    Total en DOLARES: $ {result['total_dolares']:,.2f}")
    print(f"    Promedio por documento: S/. {result['promedio_soles']:,.2f}")
    print(f"    Maximo documento: S/. {result['maximo_soles']:,.2f}")

    print()
    print("-" * 70)
    print("DISTRIBUCION POR EMPRESA (ACEPTANTE)")
    print("-" * 70)
    empresas = test_distribucion_empresas()
    for emp, datos in list(empresas.items())[:5]:
        print(
            f"    {emp}: S/. {datos['IMPORTE']:,.0f} ({datos['Nº LETRA - FACT']} docs)"
        )

    print()
    print("-" * 70)
    print("DISTRIBUCION POR PRODUCTO (TOP 10)")
    print("-" * 70)
    productos = test_distribucion_productos()
    for prod, monto in list(productos.items())[:10]:
        print(f"    {prod}: S/. {monto:,.2f}")

    print()
    print("-" * 70)
    print("ANALISIS DE RIESGO DE CONCENTRACION")
    print("-" * 70)
    riesgo = test_riesgo_concentracion()
    print(f"    Total empresas: {riesgo['total_empresas']}")
    if riesgo["alto_riesgo"]:
        print(
            f"    ALERTA: {len(riesgo['alto_riesgo'])} empresas con >40% concentracion:"
        )
        for emp, datos in riesgo["alto_riesgo"].items():
            print(f"      - {emp}: {datos['porcentaje']:.1f}%")

    print()
    print("=" * 70)
    print("AUDITORIA COMPLETADA")
    print("=" * 70)

    return True


if __name__ == "__main__":
    run_auditoria_completa()
