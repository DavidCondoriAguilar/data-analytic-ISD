import openpyxl
from pathlib import Path

EXCEL_PATH = Path(r"c:\Users\porra\OneDrive\Escritorio\DATA-Analytic\data-analytic-ISD\data\clean\data-main\SALDO - FLUJO DE PAGOS 2026.xlsx")
wb = openpyxl.load_workbook(str(EXCEL_PATH), read_only=False)

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    dvs = ws.data_validations.dataValidation
    if dvs:
        print(f"Sheet '{sheet_name}' has {len(dvs)} data validations")
        for dv in dvs:
            print(f"  Type: {dv.type}, Formula: {dv.formula1}, Cells: {dv.sqref}")
    else:
        print(f"Sheet '{sheet_name}' has no data validations")
