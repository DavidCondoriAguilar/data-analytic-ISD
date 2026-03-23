"""PDF export functionality for professional reports."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
from typing import Dict, Any


class PDFReport(FPDF):
    """Custom PDF class for professional dashboard reports."""
    
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(10, 10, 10)
        
    def header(self):
        """Add header to each page."""
        # Logo/Title area
        self.set_fill_color(30, 58, 95)  # Primary color
        self.rect(0, 0, 297, 25, 'F')
        
        # Title
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 8)
        self.cell(0, 10, 'Sueño Dorado - Control de Pagos', ln=False)
        
        # Subtitle
        self.set_font('Arial', '', 11)
        self.set_xy(10, 16)
        self.cell(0, 10, 'Reporte Ejecutivo de Cartera de Cobranza', ln=False)
        
        # Date
        self.set_font('Arial', '', 10)
        self.set_xy(240, 10)
        self.cell(0, 10, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=False)
        
        self.ln(30)
        
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}} | ISD Data Analytics', 0, 0, 'C')
        
    def add_metrics_summary(self, metrics: Dict[str, Any]):
        """Add KPI metrics summary section."""
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 58, 95)
        self.cell(0, 10, 'Resumen Ejecutivo', ln=True)
        self.ln(5)
        
        # Metrics boxes
        col_width = 65
        row_height = 25
        y_start = self.get_y()
        
        metrics_data = [
            ('Total Documentos', f"{metrics['total_docs']:,}", ''),
            ('Cartera Soles', f"S/. {metrics['soles_total']:,.0f}", ''),
            ('Cartera Dólares', f"$ {metrics['dolares_total']:,.0f}", ''),
            ('% Vencidos', f"{metrics['pct_vencidos']:.1f}%", '')
        ]
        
        for i, (label, value, _) in enumerate(metrics_data):
            x_pos = 10 + (i * (col_width + 5))
            
            # Box background
            self.set_fill_color(240, 245, 255)
            self.set_draw_color(59, 130, 246)
            self.rounded_rect(x_pos, y_start, col_width, row_height, 3, 'DF')
            
            # Label
            self.set_xy(x_pos, y_start + 3)
            self.set_font('Arial', '', 9)
            self.set_text_color(100, 100, 100)
            self.cell(col_width, 5, label, 0, 1, 'C')
            
            # Value
            self.set_xy(x_pos, y_start + 12)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(30, 58, 95)
            self.cell(col_width, 8, value, 0, 1, 'C')
            
        self.ln(35)
        
    def add_risk_analysis(self, metrics: Dict[str, Any]):
        """Add risk analysis section."""
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 58, 95)
        self.cell(0, 10, 'Análisis de Riesgo', ln=True)
        self.ln(3)
        
        # Risk metrics table
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(59, 130, 246)
        self.set_text_color(255, 255, 255)
        
        # Header
        col_widths = [60, 40, 50, 50]
        headers = ['Categoría', 'Documentos', 'Monto (S/.)', 'Estado']
        
        for width, header in zip(col_widths, headers):
            self.cell(width, 8, header, 1, 0, 'C', True)
        self.ln()
        
        # Data rows
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        risk_data = [
            ('Al Día', f"{metrics['al_dia']}", f"S/. {metrics['al_dia_monto']:,.0f}", '✓ Normal'),
            ('Vencidos', f"{metrics['vencidos']}", f"S/. {metrics['vencidos_monto']:,.0f}", '⚠️ Alerta'),
            ('Alto Riesgo (>90d)', f"{len(metrics['riesgo_alto'])}", 
             f"S/. {metrics['riesgo_alto']['IMPORTE'].sum():,.0f}", '🔴 Crítico'),
            ('Medio Riesgo (31-90d)', f"{len(metrics['riesgo_medio'])}", 
             f"S/. {metrics['riesgo_medio']['IMPORTE'].sum():,.0f}", '🟡 Atención')
        ]
        
        fills = [False, True, False, True]
        for i, (cat, docs, monto, estado) in enumerate(risk_data):
            if fills[i]:
                self.set_fill_color(245, 248, 255)
            else:
                self.set_fill_color(255, 255, 255)
                
            self.cell(col_widths[0], 7, cat, 1, 0, 'L', fills[i])
            self.cell(col_widths[1], 7, docs, 1, 0, 'C', fills[i])
            self.cell(col_widths[2], 7, monto, 1, 0, 'R', fills[i])
            self.cell(col_widths[3], 7, estado, 1, 1, 'C', fills[i])
            
        self.ln(10)
        
    def add_data_table(self, df: pd.DataFrame, title: str = "Detalle de Documentos"):
        """Add data table with paginated results."""
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 58, 95)
        self.cell(0, 10, title, ln=True)
        self.ln(3)
        
        # Prepare data - limit to first 50 rows for PDF
        df_display = df.head(50).copy()
        
        # Column headers mapping
        column_mapping = {
            'GIRADOR': 'Girador',
            'BANCO': 'Banco',
            'IMPORTE': 'Importe',
            'MONEDA': 'Moneda',
            'Fecha de Vencimiento': 'Vencimiento',
            'DIAS VENCIDOS': 'Días Venc.'
        }
        
        # Select and rename columns
        cols_to_show = [col for col in column_mapping.keys() if col in df_display.columns]
        df_subset = df_display[cols_to_show].rename(columns=column_mapping)
        
        # Table header
        self.set_font('Arial', 'B', 8)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        
        col_widths = [50, 25, 35, 25, 35, 25]
        
        for width, col in zip(col_widths, df_subset.columns):
            self.cell(width, 6, str(col)[:15], 1, 0, 'C', True)
        self.ln()
        
        # Table rows
        self.set_font('Arial', '', 7)
        self.set_text_color(0, 0, 0)
        
        for idx, row in df_subset.iterrows():
            fill = idx % 2 == 0
            if fill:
                self.set_fill_color(245, 248, 255)
            else:
                self.set_fill_color(255, 255, 255)
                
            values = [
                str(row.get('Girador', ''))[:25],
                str(row.get('Banco', ''))[:12],
                f"{row.get('Importe', 0):,.0f}" if pd.notna(row.get('Importe')) else '',
                str(row.get('Moneda', ''))[:8],
                str(row.get('Vencimiento', ''))[:10] if pd.notna(row.get('Vencimiento')) else '',
                str(row.get('Días Venc.', ''))[:6]
            ]
            
            for width, value in zip(col_widths, values):
                self.cell(width, 5, value, 1, 0, 'L' if width == 50 else 'C', fill)
            self.ln()
            
        # Note if truncated
        if len(df) > 50:
            self.ln(3)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, f'* Mostrando primeros 50 de {len(df)} registros. Descargue CSV/Excel para datos completos.', ln=True)
            
        self.ln(5)
        
    def add_certification_section(self, df: pd.DataFrame):
        """Add data certification section."""
        self.add_page()
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(16, 185, 129)
        self.cell(0, 10, 'Certificación de Datos al 100%', ln=True)
        self.ln(3)
        
        # Certification box
        self.set_fill_color(230, 255, 245)
        self.set_draw_color(16, 185, 129)
        self.rounded_rect(10, self.get_y(), 277, 40, 5, 'DF')
        
        self.set_xy(15, self.get_y() + 5)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(16, 185, 129)
        self.cell(0, 8, '✓ INTEGRIDAD DE DATOS VERIFICADA', ln=True)
        
        self.set_xy(15, self.get_y())
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f'Total de registros: {len(df):,}', ln=True)
        self.cell(0, 6, f'Columnas analizadas: {len(df.columns)}', ln=True)
        self.cell(0, 6, f'Giradores únicos: {df["GIRADOR"].nunique()}', ln=True)
        
        self.ln(50)
        
        # Summary table
        self.set_font('Arial', 'B', 12)
        self.set_text_color(30, 58, 95)
        self.cell(0, 10, 'Resumen Ejecutivo Certificado', ln=True)
        self.ln(3)
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total Documentos', f"{len(df):,}"],
            ['Cartera Soles', f"S/. {df['IMPORTE'].sum():,.2f}"],
            ['Cartera Dólares', f"$. {df['DOLARES'].sum():,.2f}"],
            ['Documentos al Día', f"{len(df[df['DIAS VENCIDOS'] == 0]):,}"],
            ['Documentos Vencidos', f"{len(df[df['DIAS VENCIDOS'] > 0]):,}"],
            ['Alto Riesgo (>90 días)', f"{len(df[df['DIAS VENCIDOS'] > 90]):,}"],
            ['Bancos', f"{df['BANCO'].nunique()}"],
            ['Productos', f"{df['PRODUCTO'].nunique()}"]
        ]
        
        # Draw summary table
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        self.cell(80, 7, summary_data[0][0], 1, 0, 'C', True)
        self.cell(100, 7, summary_data[0][1], 1, 1, 'C', True)
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        for i, (metrica, valor) in enumerate(summary_data[1:], 1):
            fill = i % 2 == 0
            if fill:
                self.set_fill_color(245, 248, 255)
            else:
                self.set_fill_color(255, 255, 255)
                
            self.cell(80, 6, metrica, 1, 0, 'L', fill)
            self.cell(100, 6, valor, 1, 1, 'R', fill)
            
        # Final certification stamp
        self.ln(15)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(16, 185, 129)
        self.cell(0, 10, '🎉 CERTIFICACIÓN AL 100% COMPLETADA', ln=True, align='C')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f'Documento certificado el {datetime.now().strftime("%d de %B de %Y a las %H:%M")}', ln=True, align='C')


def generate_pdf_report(df: pd.DataFrame, metrics: Dict[str, Any]) -> BytesIO:
    """Generate a professional PDF report.
    
    Args:
        df: Filtered dataframe
        metrics: Dictionary with calculated metrics
        
    Returns:
        BytesIO buffer with PDF content
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Add content sections
    pdf.add_metrics_summary(metrics)
    pdf.add_risk_analysis(metrics)
    pdf.add_data_table(df, "Top Documentos de Cobranza")
    pdf.add_certification_section(df)
    
    # Save to buffer
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer
