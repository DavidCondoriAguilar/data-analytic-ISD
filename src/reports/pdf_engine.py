from io import BytesIO
from datetime import datetime
import pandas as pd
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generar_pdf_profesional(df_f, tipo_cambio, totales, filtros_info):
    """Genera un reporte PDF con diseño ejecutivo y tablas detalladas."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Configuración de Colores Corporativos
    PRIMARY = "#0a1628"
    ACCENT = "#3b82f6"
    SUCCESS = "#10b981"
    GRAY = "#64748b"

    # 1. Header Principal
    periodo = filtros_info.get("periodo", "Todo")
    bancos = filtros_info.get("bancos", "Todos")
    
    header_data = [
        ["SUEÑO DORADO - DASHBOARD", f"Periodo: {periodo}", datetime.now().strftime("%d %b %Y")],
        ["Reporte Certificado de Cartera", f"Bancos: {bancos}", f"TC: S/. {tipo_cambio:.2f}"],
    ]
    header_table = Table(header_data, colWidths=[250, 300, 100])
    header_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 16),
        ("TEXTCOLOR", (0, 0), (0, -1), rl_colors.HexColor(PRIMARY)),
        ("LINEBELOW", (0, 1), (-1, 1), 2, rl_colors.HexColor(ACCENT)),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # 2. Resumen Ejecutivo (Métricas)
    metrics_data = [[
        f"{totales['total_docs']}\nDocumentos",
        f"S/. {totales['soles']:,.0f}\nSoles",
        f"$ {totales['dolares']:,.0f}\nDolares",
        f"$ {totales['total_usd']:,.0f}\nTotal USD",
        f"{totales['pct_venc']:.1f}%\nMora",
    ]]
    metrics_table = Table(metrics_data, colWidths=[120] * 5)
    metrics_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), rl_colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 25))

    # 3. Distribución por Banco
    por_banco = df_f.groupby("BANCO").agg({"IMPORTE": "sum", "NUMERO UNICO": "count"}).reset_index().sort_values("IMPORTE", ascending=False)
    banco_header = [["BANCO", "DOCUMENTOS", "MONTO ACUMULADO"]]
    for _, row in por_banco.iterrows():
        banco_header.append([str(row["BANCO"])[:30], str(row["NUMERO UNICO"]), f"S/. {row['IMPORTE']:,.2f}"])
    
    banco_table = Table(banco_header, colWidths=[200, 100, 150])
    banco_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(PRIMARY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor("#f8fafc")]),
    ]))
    elements.append(Paragraph("DISTRIBUCIÓN POR BANCO", styles["Heading3"]))
    elements.append(banco_table)
    elements.append(Spacer(1, 20))

    # 4. Detalle de Documentos (Top 150)
    elements.append(Paragraph("DETALLE EXHAUSTIVO DE DOCUMENTOS", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    detalle_header = [["ID", "GIRADOR", "FECHA VENC", "DIAS", "MON", "IMPORTE"]]
    for _, row in df_f.head(150).iterrows():
        fecha_v = row["Fecha de Vencimiento"].strftime("%d/%m/%Y") if pd.notna(row["Fecha de Vencimiento"]) else "-"
        detalle_header.append([
            str(row["NUMERO UNICO"])[:12], 
            str(row["GIRADOR"])[:25], 
            fecha_v, 
            f"{int(row['DIAS VENCIDOS'])}d", 
            str(row["MONEDA"]), 
            f"{row['IMPORTE']:,.2f}"
        ])
    
    detalle_table = Table(detalle_header, colWidths=[80, 180, 80, 50, 40, 80])
    detalle_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor(GRAY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#e2e8f0")),
    ]))
    elements.append(detalle_table)
    
    if len(df_f) > 150:
        elements.append(Paragraph(f"... y {len(df_f)-150} documentos mas no listados por espacio.", styles["Italic"]))

    # Finalizar
    doc.build(elements)
    buffer.seek(0)
    return buffer
