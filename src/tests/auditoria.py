"""
AUDITORÍA DE DATOS - Sueño Dorado / ISD
========================================
Test simple para verificar que los cálculos son correctos.
"""

import pandas as pd


def cargar_datos_auditoria():
    """Carga datos igual que app.py"""
    excel_path = "data/clean/data-main/SALDO - FLUJO DE PAGOS 2026.xlsx"
    df = pd.read_excel(excel_path, sheet_name="DATA ORIGINAL", header=2)
    df = df[df["CONDICION DEUDA"] == "PENDIENTE DE PAGO"]
    df = df[df["IMPORTE"].notna()]

    if "NUMERO UNICO" in df.columns:
        mask = df["NUMERO UNICO"].isna()
        nuevo_numero = df.loc[mask, "Nº LETRA - FACT"].fillna("")
        vacios = nuevo_numero == ""
        nuevo_numero.loc[vacios] = "S/N-" + df.loc[mask][vacios].index.astype(str)
        df.loc[mask, "NUMERO UNICO"] = nuevo_numero

    df["IMPORTE"] = pd.to_numeric(
        df["IMPORTE"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DOLARES"] = pd.to_numeric(
        df["DOLARES"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["DIAS VENCIDOS"] = pd.to_numeric(
        df["DIAS VENCIDOS"].astype(str).str.replace(",", ""), errors="coerce"
    )

    return df


def calcular_totales(df):
    """Calcula totales igual que el dashboard"""
    soles = df[df["MONEDA"] == "SOLES"]["IMPORTE"].sum()
    dolares = df[df["MONEDA"] == "DOLARES"]["IMPORTE"].sum()
    tipo_cambio = 3.45

    importe_usd = soles / tipo_cambio + dolares

    return {
        "total_documentos": len(df),
        "total_soles": soles,
        "total_dolares": dolares,
        "total_usd": importe_usd,
        "vencidos": len(df[df["DIAS VENCIDOS"] > 0]),
        "al_dia": len(df[df["DIAS VENCIDOS"] == 0]),
        "por_vencer": len(df[df["DIAS VENCIDOS"] < 0]),
    }


def main():
    print("=" * 60)
    print("AUDITORÍA DE DATOS - Sueño Dorado / ISD")
    print("=" * 60)

    df = cargar_datos_auditoria()
    totales = calcular_totales(df)

    print(f"\nDATOS CARGADOS:")
    print(f"   Total documentos: {totales['total_documentos']}")
    print(f"   Total Soles: S/. {totales['total_soles']:,.2f}")
    print(f"   Total Dolares: $ {totales['total_dolares']:,.2f}")
    print(f"   Total USD (equivalente): $ {totales['total_usd']:,.2f}")

    print(f"\nCLASIFICACION POR VENCIMIENTO:")
    print(f"   Vencidos (>0 dias): {totales['vencidos']}")
    print(f"   Al dia (=0 dias): {totales['al_dia']}")
    print(f"   Por vencer (<0 dias): {totales['por_vencer']}")

    suma_estados = totales["vencidos"] + totales["al_dia"] + totales["por_vencer"]
    print(f"\nVERIFICACION: {suma_estados} == {totales['total_documentos']} ? ", end="")
    print("OK" if suma_estados == totales["total_documentos"] else "ERROR")

    print("\n" + "=" * 60)

    return totales


if __name__ == "__main__":
    main()
