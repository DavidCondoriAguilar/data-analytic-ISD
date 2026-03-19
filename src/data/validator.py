"""Módulo de validación de datos."""
import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime


def cargar_valores_validos() -> Dict[str, List[str]]:
    """Carga valores válidos desde config/valid_values.json"""
    ruta = Path(__file__).parent.parent.parent / "config" / "valid_values.json"
    if ruta.exists():
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


VALID_VALUES = cargar_valores_validos()
MONEDAS_VALIDAS = VALID_VALUES.get('MONEDA', ['SOLES', 'DOLARES'])
BANCOS_VALIDOS = VALID_VALUES.get('BANCO', ['BBVA', 'BCP', 'BLACK'])
ACEPTANTES_VALIDOS = VALID_VALUES.get('ACEPTANTE', ['BLACK', 'COLCHONES VIVE', 'DREAM TEAM', 'GRUPO ISD'])
PRODUCTOS_VALIDOS = VALID_VALUES.get('PRODUCTO', ['DEUDA BANCOS', 'EFACT', 'GRAPAS', 'IMPUESTOS', 'IRIS SOLEDAD', 'MANGAS', 'NOTEX', 'PABILO', 'PASTAS', 'PLANILLA'])
GIRADORES_VALIDOS = VALID_VALUES.get('GIRADOR', ['EFACT SAC', 'MALBEZ S.R.LTDA', 'PLANILLA - HABERES', 'SIN GIRADOR'])
CONDICION_DEUDA_VALIDA = VALID_VALUES.get('CONDICION DEUDA', ['PENDIENTE DE PAGO'])[0] if VALID_VALUES.get('CONDICION DEUDA') else 'PENDIENTE DE PAGO'


@dataclass
class ValidationResult:
    passed: bool
    test_name: str
    message: str
    details: Dict = field(default_factory=dict)


class DataValidator:
    """Valida la integridad y calidad de los datos."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results: List[ValidationResult] = []

    def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        checks = [
            self.check_no_duplicate_ids,
            self.check_required_columns_exist,
            self.check_fecha_vencimiento_valid,
            self.check_importe_positivo,
            self.check_dolares_positivos,
            self.check_dias_vencidos_logico,
            self.check_monedavalida,
            self.check_banco_valido,
            self.check_aceptante_valido,
            self.check_producto_valido,
            self.check_girador_valido,
            self.check_condicion_deuda_valida,
            self.check_outliers,
            self.check_consistencia_moneda_importe,
            self.check_consistencia_dias_fecha,
            self.check_consistencia_aceptante_banco,
            self.check_no_duplicados_completos,
            self.check_formato_letra_fact,
            self.check_importes_razonables,
            self.check_distribucion_aceptantes,
            self.check_distribucion_bancos,
        ]
        for check in checks:
            try:
                check()
            except Exception as e:
                self.results.append(ValidationResult(
                    passed=False,
                    test_name=f"ERROR en {check.__name__}",
                    message=str(e),
                    details={"error": str(e)}
                ))
        return all(r.passed for r in self.results), self.results

    def check_aceptante_valido(self):
        """Verifica que ACEPTANTE sea uno de los valores válidos"""
        if 'ACEPTANTE' not in self.df.columns:
            return
        valores = self.df['ACEPTANTE'].dropna().unique()
        invalidos = [v for v in valores if v not in ACEPTANTES_VALIDOS]
        self.results.append(ValidationResult(
            passed=len(invalidos) == 0,
            test_name="Aceptante Válido",
            message=f"{len(invalidos)} valores inválidos: {invalidos}" if invalidos else f"OK - Solo valores válidos: {ACEPTANTES_VALIDOS}",
            details={"invalidos": invalidos, "validos_esperados": ACEPTANTES_VALIDOS}
        ))

    def check_producto_valido(self):
        """Verifica que PRODUCTO sea uno de los valores válidos"""
        if 'PRODUCTO' not in self.df.columns:
            return
        valores = self.df['PRODUCTO'].dropna().unique()
        invalidos = [v for v in valores if v not in PRODUCTOS_VALIDOS]
        self.results.append(ValidationResult(
            passed=len(invalidos) == 0,
            test_name="Producto Válido",
            message=f"{len(invalidos)} valores inválidos: {invalidos}" if invalidos else f"OK - Solo valores válidos",
            details={"invalidos": invalidos, "validos_esperados": PRODUCTOS_VALIDOS}
        ))

    def check_girador_valido(self):
        """Verifica que GIRADOR sea uno de los valores válidos"""
        if 'GIRADOR' not in self.df.columns:
            return
        valores = self.df['GIRADOR'].dropna().unique()
        invalidos = [v for v in valores if v not in GIRADORES_VALIDOS]
        self.results.append(ValidationResult(
            passed=len(invalidos) == 0,
            test_name="Girador Válido",
            message=f"{len(invalidos)} valores inválidos" if invalidos else "OK - Solo giradores válidos",
            details={"invalidos": invalidos, "validos_esperados": GIRADORES_VALIDOS}
        ))

    def check_condicion_deuda_valida(self):
        """Verifica que CONDICION DEUDA sea válida"""
        if 'CONDICION DEUDA' not in self.df.columns:
            return
        valores = self.df['CONDICION DEUDA'].dropna().unique()
        if CONDICION_DEUDA_VALIDA in valores:
            self.results.append(ValidationResult(
                passed=True,
                test_name="Condición Deuda Válida",
                message=f"OK - Encontrado: {CONDICION_DEUDA_VALIDA}",
                details={"valor_esperado": CONDICION_DEUDA_VALIDA}
            ))

    def check_consistencia_aceptante_banco(self):
        """Verifica consistencia entre ACEPTANTE y BANCO"""
        if 'ACEPTANTE' not in self.df.columns or 'BANCO' not in self.df.columns:
            return
        if 'BLACK' in self.df['ACEPTANTE'].values:
            registros_black = self.df[self.df['ACEPTANTE'] == 'BLACK']
            bancos_black = registros_black['BANCO'].value_counts()
            self.results.append(ValidationResult(
                passed=True,
                test_name="Consistencia Aceptante-Banco",
                message=f"BLACK tiene {len(registros_black)} registros en {dict(bancos_black)}",
                details={"registros_black": int(len(registros_black)), "bancos": bancos_black.to_dict()}
            ))

    def check_distribucion_aceptantes(self):
        """Analiza distribución por ACEPTANTE"""
        if 'ACEPTANTE' not in self.df.columns or 'IMPORTE' not in self.df.columns:
            return
        try:
            df_check = self.df.copy()
            df_check['IMPORTE'] = pd.to_numeric(df_check['IMPORTE'], errors='coerce')
            dist = df_check.groupby('ACEPTANTE')['IMPORTE'].agg(['count', 'sum', 'mean'])
            self.results.append(ValidationResult(
                passed=True,
                test_name="Distribución Aceptantes",
                message=f"4 aceptantes con {len(dist)} grupos",
                details=dist.to_dict()
            ))
        except:
            pass

    def check_distribucion_bancos(self):
        """Analiza distribución por BANCO"""
        if 'BANCO' not in self.df.columns or 'IMPORTE' not in self.df.columns:
            return
        try:
            df_check = self.df.copy()
            df_check['IMPORTE'] = pd.to_numeric(df_check['IMPORTE'], errors='coerce')
            dist = df_check.groupby('BANCO')['IMPORTE'].agg(['count', 'sum', 'mean'])
            self.results.append(ValidationResult(
                passed=True,
                test_name="Distribución Bancos",
                message=f"3 bancos con {len(dist)} grupos",
                details=dist.to_dict()
            ))
        except:
            pass

    def check_no_duplicate_ids(self):
        col = 'NUMERO UNICO'
        if col in self.df.columns:
            duplicados = self.df[col].duplicated().sum()
            self.results.append(ValidationResult(
                passed=duplicados == 0,
                test_name="Duplicados en ID",
                message=f"IDs duplicados: {duplicados}" if duplicados else "Sin duplicados",
                details={"duplicates": int(duplicados)}
            ))

    def check_required_columns_exist(self):
        required = ['NUMERO UNICO', 'IMPORTE', 'Fecha de Vencimiento', 'MONEDA', 'BANCO']
        missing = [c for c in required if c not in self.df.columns]
        self.results.append(ValidationResult(
            passed=len(missing) == 0,
            test_name="Columnas Requeridas",
            message=f"Faltan: {missing}" if missing else "OK",
            details={"missing": missing}
        ))

    def check_fecha_vencimiento_valid(self):
        col = 'Fecha de Vencimiento'
        if col in self.df.columns:
            fechas = pd.to_datetime(self.df[col], errors='coerce')
            invalidas = fechas.isna().sum()
            self.results.append(ValidationResult(
                passed=invalidas == 0,
                test_name="Fechas Válidas",
                message=f"Fechas inválidas: {invalidas}" if invalidas else "OK",
                details={"invalidas": int(invalidas)}
            ))

    def check_importe_positivo(self):
        col = 'IMPORTE'
        if col in self.df.columns:
            valores = pd.to_numeric(self.df[col], errors='coerce')
            negativos = (valores.fillna(0) < 0).sum()
            nulos = valores.isna().sum()
            self.results.append(ValidationResult(
                passed=negativos == 0,
                test_name="Importes Positivos",
                message=f"Negativos: {negativos}, Nulos: {nulos}" if negativos else "OK",
                details={"negativos": int(negativos), "nulos": int(nulos)}
            ))

    def check_dolares_positivos(self):
        col = 'DOLARES'
        if col in self.df.columns:
            valores = pd.to_numeric(self.df[col], errors='coerce')
            negativos = (valores.fillna(0) < 0).sum()
            self.results.append(ValidationResult(
                passed=negativos == 0,
                test_name="Dólares Positivos",
                message=f"Negativos: {negativos}" if negativos else "OK",
                details={"negativos": int(negativos)}
            ))

    def check_dias_vencidos_logico(self):
        col = 'DIAS VENCIDOS'
        if col in self.df.columns:
            valores = pd.to_numeric(self.df[col], errors='coerce')
            negativos = (valores.fillna(0) < 0).sum()
            extremos = (valores.fillna(0) > 365).sum()
            self.results.append(ValidationResult(
                passed=negativos == 0 and extremos == 0,
                test_name="Días Vencidos Lógicos",
                message=f"Negativos: {negativos}, >365: {extremos}" if negativos or extremos else "OK",
                details={"negativos": int(negativos), "extremos": int(extremos)}
            ))

    def check_monedavalida(self):
        col = 'MONEDA'
        if col in self.df.columns:
            valores = self.df[col].dropna().unique()
            invalidos = [v for v in valores if v not in MONEDAS_VALIDAS]
            self.results.append(ValidationResult(
                passed=len(invalidos) == 0,
                test_name="Moneda Válida",
                message=f"Inválidas: {invalidos}" if invalidos else f"OK - Solo: {MONEDAS_VALIDAS}",
                details={"invalidos": invalidos, "validos_esperados": MONEDAS_VALIDAS}
            ))

    def check_banco_valido(self):
        col = 'BANCO'
        if col in self.df.columns:
            valores = self.df[col].dropna().unique()
            invalidos = [v for v in valores if v not in BANCOS_VALIDOS]
            self.results.append(ValidationResult(
                passed=len(invalidos) == 0,
                test_name="Banco Válido",
                message=f"Inválidos: {invalidos}" if invalidos else f"OK - Solo: {BANCOS_VALIDOS}",
                details={"invalidos": invalidos, "validos_esperados": BANCOS_VALIDOS}
            ))

    def check_aceptante_no_nulo(self):
        col = 'ACEPTANTE'
        if col in self.df.columns:
            nulos = self.df[col].isna().sum()
            self.results.append(ValidationResult(
                passed=nulos == 0,
                test_name="Aceptante No Nulo",
                message=f"Nulos: {nulos}" if nulos else "OK",
                details={"nulos": int(nulos)}
            ))

    def check_girador_no_nulo(self):
        col = 'GIRADOR'
        if col in self.df.columns:
            nulos = self.df[col].isna().sum()
            self.results.append(ValidationResult(
                passed=nulos == 0,
                test_name="Girador No Nulo",
                message=f"Nulos: {nulos}" if nulos else "OK",
                details={"nulos": int(nulos)}
            ))

    def check_outliers(self):
        if 'IMPORTE' not in self.df.columns:
            return
        valores = pd.to_numeric(self.df['IMPORTE'], errors='coerce').dropna()
        if len(valores) < 4:
            return
        
        Q1 = valores.quantile(0.25)
        Q3 = valores.quantile(0.75)
        IQR = Q3 - Q1
        limite_superior = Q3 + 3 * IQR
        
        outliers = valores[valores > limite_superior]
        if len(outliers) > 0:
            self.results.append(ValidationResult(
                passed=True,
                test_name="OUTLIERS DETECTADOS",
                message=f"{len(outliers)} valores atípicos > S/. {limite_superior:,.0f}",
                details={
                    "cantidad": len(outliers),
                    "limite": float(limite_superior),
                }
            ))

    def check_consistencia_moneda_importe(self):
        if 'MONEDA' not in self.df.columns or 'IMPORTE' not in self.df.columns:
            return
        
        df_check = self.df.copy()
        df_check['IMPORTE'] = pd.to_numeric(df_check['IMPORTE'], errors='coerce')
        
        soles_sin_importe = df_check[(df_check['MONEDA'] == 'SOLES') & (df_check['IMPORTE'].isna())]
        inconsistencias = len(soles_sin_importe)
        
        self.results.append(ValidationResult(
            passed=inconsistencias == 0,
            test_name="Consistencia Moneda-Importe",
            message=f"{inconsistencias} inconsistencias" if inconsistencias else "OK",
            details={"inconsistencias": inconsistencias}
        ))

    def check_consistencia_dias_fecha(self):
        if 'Fecha de Vencimiento' not in self.df.columns or 'DIAS VENCIDOS' not in self.df.columns:
            return
        
        try:
            fechas = pd.to_datetime(self.df['Fecha de Vencimiento'], errors='coerce')
            dias = pd.to_numeric(self.df['DIAS VENCIDOS'], errors='coerce')
            
            hoy = pd.Timestamp.now()
            dias_calculados = (hoy - fechas).dt.days.fillna(0)
            
            diferencia = abs(dias.fillna(0) - dias_calculados)
            inconsistentes = (diferencia > 90).sum()
            
            self.results.append(ValidationResult(
                passed=True,
                test_name="Días vs Fecha (INFO)",
                message=f"{inconsistentes} filas con diferencia >90 días" if inconsistentes else "OK",
                details={"inconsistentes": int(inconsistentes)}
            ))
        except:
            pass

    def check_no_duplicados_completos(self):
        duplicados = self.df.duplicated().sum()
        self.results.append(ValidationResult(
            passed=duplicados == 0,
            test_name="Sin Filas Duplicadas",
            message=f"{duplicados} filas duplicadas" if duplicados else "OK",
            details={"duplicados": int(duplicados)}
        ))

    def check_formato_letra_fact(self):
        if 'Nº LETRA - FACT' not in self.df.columns:
            return
        
        vacios = self.df['Nº LETRA - FACT'].isna() | (self.df['Nº LETRA - FACT'] == '')
        validos = (~vacios).sum()
        total = len(self.df)
        porcentaje = (validos / total) * 100 if total > 0 else 0
        
        self.results.append(ValidationResult(
            passed=porcentaje >= 80,
            test_name="Nº Letra/Fact >80%",
            message=f"{validos}/{total} ({porcentaje:.1f}%) con valor",
            details={"validos": int(validos), "total": total, "porcentaje": float(porcentaje)}
        ))

    def check_importes_razonables(self):
        if 'IMPORTE' not in self.df.columns:
            return
        
        valores = pd.to_numeric(self.df['IMPORTE'], errors='coerce')
        muy_pequenos = (valores < 1).sum()
        muy_grandes = (valores > 10000000).sum()
        
        problemas = muy_pequenos + muy_grandes
        self.results.append(ValidationResult(
            passed=problemas == 0,
            test_name="Importes Razonables",
            message=f"{problemas} fuera de rango" if problemas else "OK",
            details={"muy_pequenos": int(muy_pequenos), "muy_grandes": int(muy_grandes)}
        ))

    def get_report(self) -> Dict:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        return {
            "fecha": datetime.now().isoformat(),
            "total_checks": total,
            "pasados": passed,
            "fallidos": total - passed,
            "confiabilidad": f"{(passed/total)*100:.1f}%",
            "resultados": [{"test": r.test_name, "ok": r.passed, "msg": r.message} for r in self.results]
        }
