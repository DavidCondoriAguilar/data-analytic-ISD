"""Script CLI para ejecutar pipeline de limpieza de datos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.data.cleaner import DataCleaner
from src.data.audit import AuditLogger, ConfiabilidadTracker, DataQualityAlert


def main():
    audit = AuditLogger("pipeline_ejecucion")
    audit.info("Iniciando pipeline de limpieza", {"version": "2.0"})

    print("="*60)
    print("SUEÑO DORADO - PIPELINE DE LIMPIEZA DE DATOS")
    print("="*60)

    audit.info("Cargando datos")
    print("\n[1/5] Cargando datos...")
    loader = DataLoader()
    df = loader.cargar()
    print(f"    ✓ {len(df)} filas cargadas")
    audit.info(f"Datos cargados", {"filas": len(df)})

    print("\n[2/5] Validando datos (estado inicial)...")
    validator = DataValidator(df)
    passed, results = validator.validate_all()
    report_pre = validator.get_report()
    
    confiabilidad_pre = float(report_pre['confiabilidad'].replace('%', ''))
    print(f"    Confiabilidad inicial: {report_pre['confiabilidad']}")
    audit.info("Validación inicial completada", {"confiabilidad": confiabilidad_pre})

    issues_pre = [r.message for r in results if not r.passed]
    if issues_pre:
        audit.warning("Problemas detectados en validación inicial", {"problemas": issues_pre})
        for r in results:
            if not r.passed:
                print(f"    ✗ {r.test_name}: {r.message}")
    else:
        print("    ✓ Sin problemas detectados")

    print("\n[3/5] Limpiando datos...")
    cleaner = DataCleaner(df)
    df_limpio, correcciones = cleaner.limpiar_todo()
    
    for corr in correcciones:
        print(f"    ⚙ {corr['descripcion']}")
    
    audit.info("Limpieza completada", {"correcciones": len(correcciones)})

    print("\n[4/5] Validando datos (estado final)...")
    validator2 = DataValidator(df_limpio)
    passed2, results2 = validator2.validate_all()
    report_post = validator2.get_report()
    
    confiabilidad_post = float(report_post['confiabilidad'].replace('%', ''))
    print(f"    Confiabilidad final: {report_post['confiabilidad']}")

    issues_post = [r.message for r in results2 if not r.passed]
    if issues_post:
        for r in results2:
            if not r.passed:
                print(f"    ✗ {r.test_name}: {r.message}")
    else:
        print("    ✓ Sin problemas detectados")

    ruta_csv = cleaner.guardar_csv()
    ruta_xlsx = cleaner.guardar_excel()
    print(f"\n[5/5] Guardando archivos...")
    print(f"    📁 CSV: {Path(ruta_csv).name}")
    print(f"    📁 XLSX: {Path(ruta_xlsx).name}")

    audit.success("Pipeline completado", {
        "confiabilidad_inicial": confiabilidad_pre,
        "confiabilidad_final": confiabilidad_post,
        "filas_originales": len(df),
        "filas_limpias": len(df_limpio),
        "correcciones": len(correcciones),
        "archivo_csv": str(ruta_csv),
        "archivo_xlsx": str(ruta_xlsx)
    })

    ConfiabilidadTracker.record(
        confiabilidad=confiabilidad_post,
        total_records=len(df),
        valid_records=len(df_limpio),
        source_file="SALDO - FLUJO DE PAGOS 2026.xlsx",
        issues=issues_post
    )
    audit.info("Historial de confiabilidad actualizado")

    alert = DataQualityAlert.check_and_alert(confiabilidad_post, threshold=99.9)
    if alert:
        print(f"\n    🚨 ALERTA: {alert['message']}")
        audit.error("Alerta de calidad generada", alert)

    audit.save_summary()

    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Filas originales:   {len(df)}")
    print(f"Filas limpiadas:    {len(df_limpio)}")
    print(f"Correcciones:       {len(correcciones)}")
    print(f"Confiabilidad:      {confiabilidad_pre:.1f}% → {confiabilidad_post:.1f}%")
    print(f"Certificado:       {'✓ SÍ' if confiabilidad_post >= 99.9 else '✗ NO'}")
    print("="*60)

    return df_limpio


if __name__ == "__main__":
    main()
