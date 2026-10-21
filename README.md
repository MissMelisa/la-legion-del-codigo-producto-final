# La Legión del Código — Gestión y análisis de precios (Córdoba)

Proyecto Integrador ABP · Tecnicatura Superior en Ciencia de Datos e IA (ISPC)
Programación I y Bases de Datos II.

Aplicación de consola en Python (POO + MySQL) para gestionar productos y
consultar precios por sucursal, más un módulo de análisis con Pandas y
NumPy que responde:

> **¿Qué diferencias de precio presenta un mismo producto entre sucursales
> de Córdoba y cómo pueden utilizarse para orientar decisiones comerciales?**

Datos: Precios Claros (SEPA), sucursales de Córdoba (AR-X), abril–mayo de
2020. Es una muestra histórica: **no son precios vigentes**.

Integrantes: Ríos, Paula Melisa · Tauil, Maximiliano · Parisi, Julián ·
Saravia Weht, Guadalupe Regina.

---

## LÉAME: instalación y ejecución

### Requisitos

- Python 3.11 o superior
- MySQL 8.0 o superior (servidor local o remoto) y el cliente `mysql`
  o MySQL Workbench

### 1. Descargar el proyecto e instalar dependencias

```bash
git clone <URL-del-repositorio>
cd la-legion-del-codigo-producto-final

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar la conexión (sin credenciales en el repositorio)

```bash
cp .env.ejemplo .env               # Windows: copy .env.ejemplo .env
```

Editá `.env` y completá `MYSQL_PASSWORD` (y el resto si tu MySQL no usa
los valores por defecto). El archivo `.env` está en `.gitignore`: **no se
sube ni se entrega**.

### 3. Crear y cargar la base de datos

Un único script crea la base `datos_comercios`, las tablas, carga los
99.681 precios y crea las vistas:

```bash
mysql -u root -p < sql/datos_comercios.sql
```

En MySQL Workbench: *File → Run SQL Script…* y elegir
`sql/datos_comercios.sql`.

Al terminar se muestra la verificación:

| tabla | cantidad |
|---|---|
| productos | 22565 |
| sucursales | 163 |
| precios | 99681 |

> El script empieza con `DROP DATABASE IF EXISTS datos_comercios`: se
> puede volver a ejecutar cuantas veces haga falta y siempre deja la base
> en el mismo estado inicial (borra los cambios hechos desde el menú).

### 4. Abrir la aplicación

```bash
python main.py
```

| Opción | Qué hace |
|---|---|
| 1 | Alta de producto (valida el código y permite cargar un precio en una sucursal) |
| 2 | Baja de producto (borra el producto y sus precios en una transacción) |
| 3 | Modificación de producto |
| 4 | Búsqueda por nombre |
| 5 | Búsqueda por categoría |
| 6 | Precios de un producto en cada sucursal (`vista_precios_detalle`) |
| 7 | Ejecutar el análisis de precios |

### 5. Ejecutar el análisis

```bash
python -m app.analisis                 # resultados + gráficos
python -m app.analisis --sin-graficos
```

Lee los datos desde MySQL y guarda en `resultados/`:

- `resumen.md`: **todas las cifras del informe y del póster** (única fuente de números)
- `p1_…`, `p2_…`, `p3_…`, `indice_por_sucursal.csv`, `valores_extremos.csv`: tablas completas
- `g1_…`, `g2_…`, `g3_…png`: gráficos

---

## Estructura

```text
.
├── main.py                     punto de entrada: abre el menú
├── app/
│   ├── conexion.py             ConexionBD (PyMySQL) + crear_engine (SQLAlchemy)
│   ├── producto_crud.py        ProductoCRUD: único acceso a la base
│   ├── menu.py                 menú de consola
│   ├── analisis.py             análisis con Pandas y NumPy
│   └── modelos/                entidades: Producto, Sucursal, Precio
├── sql/
│   └── datos_comercios.sql     script único: base + tablas + datos + vistas
├── preparacion/                (solo para regenerar los datos, ver abajo)
│   ├── limpieza.py
│   ├── categorizador.py
│   └── generar_sql.py
├── dataset/procesado/          CSV limpios (entrada de generar_sql.py)
├── resultados/                 salida del análisis
├── docs/
│   ├── recorte.md              pregunta central, preguntas y componentes
│   ├── anexo_correcciones.md   tabla de correcciones (anexo del informe)
│   └── diseno_base_datos.md    modelo relacional, calidad de datos y clases
├── requirements.txt
└── .env.ejemplo
```

### Vistas SQL

| Vista | Uso |
|---|---|
| `vista_precios_detalle` | Une productos, sucursales y precios (menú y análisis) |
| `vista_resumen_producto` | Mínimo, máximo, diferencia y variación % por producto (P2) |
| `vista_precio_minimo_producto` | Precio mínimo de cada producto y comercio donde está (P1) |
| `vista_indice_precio` | Precio relativo al promedio del mismo producto (productos en 10 o más sucursales) |
| `vista_indice_comercio` / `vista_indice_sucursal` | Índice promedio por comercio y por sucursal (P3) |

---

## Regenerar los datos desde los CSV originales (opcional)

No hace falta para instalar ni ejecutar: `sql/datos_comercios.sql` ya
incluye los datos. Solo si se quiere reproducir la limpieza:

1. Descargar de [Precios Claros / SEPA](https://datos.produccion.gob.ar/dataset/sepa-precios)
   `productos.csv`, `sucursales.csv` y los `precios_*.csv` de abril–mayo de 2020,
   y copiarlos a `dataset/` (no se versionan por su tamaño).
2. Ejecutar:

```bash
python preparacion/limpieza.py      # genera dataset/procesado/*.csv
python preparacion/generar_sql.py   # genera sql/datos_comercios.sql
```

`limpieza.py` imprime un diagnóstico de calidad (nulos, duplicados, tipos)
y aplica: filtro de Córdoba (AR-X), IDs como texto, normalización de
textos y localidades, descarte de precios inválidos, un precio por
producto + sucursal (el del archivo semanal más reciente) y categorías
inferidas por palabras clave. Detalle en
[docs/diseno_base_datos.md](docs/diseno_base_datos.md).
