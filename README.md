# Sueño Dorado - Control de Pagos

## ¿Qué hace?

Automatiza la validación y limpieza de datos de Excel para el control de cartera de pagos.

## Resultados Actuales

| Métrica | Valor |
|---------|-------|
| Registros limpiados | 160 / 171 |
| Confiabilidad | **100%** ✓ |
| Cartera Soles | S/. 3,229,280 |
| Cartera Dólares | $1,335,569 |

## Comandos

```bash
# Limpiar y certificar datos
./venv/bin/python src/data/clean_pipeline.py

# Generar reporte de certificación
./venv/bin/python src/data/certificar.py

# Ver dashboard (BI)
./venv/bin/streamlit run src/dashboard/app.py

# Ejecutar pruebas
./venv/bin/python -m pytest src/tests/ -q
```

## Proceso Automático

1. **Carga** - Lee Excel original
2. **Valida** - 21 checks de calidad
3. **Limpia** - Corrige/marca problemas
4. **Certifica** - Confirma 99.9%+ confiabilidad
5. **Alerta** - Notifica si calidad baja

## Arquitectura

```
data/raw/           → Excel original
data/clean/         → Datos certificados
reports/logs/       → Auditoría e historial
config/valid_values.json → Valores válidos (extraídos de data limpia)
```

## Validaciones Incluidas

- IDs únicos
- Fechas válidas
- Rangos lógicos (días vencidos 0-365)
- Monedas/Bancos/Giradores correctos
- Detección de outliers
- Consistencia cruzada

## Para Cambios

Si el Excel cambia, regenerar valores válidos:
```bash
./venv/bin/python -c "
import pandas as pd, json
df = pd.read_excel('data/clean/datos_limpios.xlsx')
valores = {col: sorted(df[col].dropna().str.strip().str.upper().unique().tolist()) 
           for col in ['MONEDA','BANCO','ACEPTANTE','PRODUCTO','GIRADOR']}
with open('config/valid_values.json','w') as f: json.dump(valores, f, indent=2)
"
```
