# Sueño Dorado - Control de Pagos

## Descripción
Dashboard de BI para el control de cartera de pagos de Sueño Dorado / ISD. Valida, limpia y visualiza datos de Excel con certificación de confiabilidad 99.9%.

## Características
- Dashboard interactivo con Streamlit
- Tema oscuro minimalista
- Filtros: Banco, Moneda, Girador, Fecha
- Gráficos: Evolución, Por Banco, Distribución, Antigüedad, Girador, Producto
- Descarga de reportes en CSV y Excel
- Certificación de datos 99.9%

## Deployment en Streamlit Cloud

### Paso 1: Ir a Streamlit Cloud
1. Abre: https://streamlit.io/cloud
2. Inicia sesión con tu cuenta de GitHub

### Paso 2: Deploy
1. Click en **"New app"**
2. Selecciona:
   - **Repository:** `DavidCondoriAguilar/data-analytic-ISD`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click en **"Deploy!"**

### Paso 3: Esperar
- El deploy toma ~2-3 minutos
- Recibirás una URL como: `https://tu-app.streamlit.app`

### Paso 4: Compartir
- Comparte la URL con tu gerente
- Él puede ver el dashboard desde cualquier navegador

## Desarrollo Local

```bash
# Clonar repo
git clone https://github.com/DavidCondoriAguilar/data-analytic-ISD.git
cd data-analytic-ISD

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Correr dashboard
streamlit run app.py

# Correr tests
pytest src/tests/ -q
```

## Estructura del Proyecto

```
├── app.py                    # Dashboard principal (raíz para deploy)
├── src/
│   ├── dashboard/app.py       # Dashboard (copia en src)
│   ├── data/
│   │   ├── loader.py         # Carga datos
│   │   ├── validator.py      # 21 validaciones
│   │   ├── cleaner.py        # Limpieza automática
│   │   ├── audit.py          # Logging y tracking
│   │   └── certificar.py     # Reporte de certificación
│   └── tests/                # 45 tests automatizados
├── data/clean/               # Datos certificados
├── config/                   # Configuraciones
└── requirements.txt          # Dependencias
```

## Comandos Rápidos

```bash
# Limpiar y certificar datos
python src/data/clean_pipeline.py

# Generar reporte
python src/data/certificar.py

# Ver dashboard
streamlit run app.py

# Tests
pytest src/tests/ -q
```

## Tecnologías
- Python 3.12
- Streamlit
- Pandas
- Plotly
- openpyxl

## Autor
David Condori Aguilar
