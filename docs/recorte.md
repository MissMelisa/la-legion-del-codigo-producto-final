# Recorte del producto final

Las cifras de este documento salen de `resultados/resumen.md`, que genera
`python -m app.analisis`. Si cambian los datos, se actualizan desde ahí.

## Pregunta central

Parte del hallazgo principal de la Evidencia 3 (el precio de un mismo
producto varía de forma apreciable entre sucursales):

> **¿Qué diferencias de precio presenta un mismo producto entre sucursales
> de Córdoba y cómo pueden utilizarse para orientar decisiones comerciales?**

## Preguntas de análisis elegidas (de las 5 de la Evidencia 1)

| # | Pregunta | Por qué sostiene la pregunta central |
|---|---|---|
| P1 | ¿Cuál es el precio mínimo registrado para cada producto y en qué comercio se encuentra? | Muestra dónde conviene comprar cada producto y qué comercios concentran los mínimos. |
| P2 | ¿Cuál es la diferencia entre el precio máximo y mínimo de cada producto? | Mide la magnitud de la diferencia, que es la pregunta central. |
| P3 | ¿Cuál es el precio promedio de los productos según cada comercio? | Se responde con un índice sobre productos comparables, que permite ubicar comercios y sucursales relativamente caros (base de la decisión). |

Quedan fuera del póster (siguen en el informe): precio máximo por
categoría y suma de precios por comercio, porque no comparan un mismo
producto entre sucursales.

## Criterios del análisis

- **Mismo producto** = mismo `producto_id` (código de barras). No se agrupa
  por nombre: 960 nombres son compartidos por dos o más códigos distintos.
- **Producto comparable** = con precio en al menos 10 sucursales (2.841 productos).
- **Índice relativo** = precio ÷ precio promedio de ese producto. Se
  promedia por comercio o sucursal. Un comercio o una sucursal es
  representativo si tiene al menos 100 productos comparables.
- **Valores extremos**: un precio a más de 3 veces (o a menos de 1/3) de la
  mediana de su producto se conserva, pero se marca "a contrastar".

## Resultados clave

| | Resultado |
|---|---|
| P2 | Variación máx–mín **mediana: 42,2 %** (la mitad central está entre 28,8 % y 60,5 %). El 82,0 % de los productos comparables varía más de 25 % y el 36,9 % más de 50 %. |
| P1 | Canasta de 10 productos (ej. Aceite Natura 1,5 L: $126,00 en Dinosaurio y $185,00 en INC/Libertad). Miguel Becerra tiene el mínimo en 736 productos comparables (25,9 %). |
| P3 | Con el índice, el orden de los comercios cambia: Dinosaurio tiene el **promedio simple más alto** ($223,62) pero cobra **8,6 % menos** que el promedio por los mismos productos. El más caro con muestra suficiente es Jumbo Retail (+5,2 %) y el más barato es Mariano (−10,0 %, con 1 sucursal). Pan American Energy (12 productos) y DIA (84) no tienen muestra suficiente. |
| Decisión | Las sucursales relativamente más caras (Disco Villa Allende +9,8 %, Mini Libertad Ambrosio Olmos +8,9 %, Cordiez 47 Capilla del Monte +8,7 %…) son candidatas para revisar precios o evaluar promociones en productos comparables, considerando costos y márgenes. |

## Componentes que participan

| Capa | Componente | Uso en el recorte |
|---|---|---|
| Tablas | `productos`, `sucursales`, `precios` (PK compuesta `producto_id` + `sucursal_id`) | Datos base |
| Vistas | `vista_precios_detalle` | Fuente única del análisis y del menú (opción 6) |
| | `vista_precio_minimo_producto` | P1 en SQL |
| | `vista_resumen_producto` | P2 en SQL |
| | `vista_indice_precio`, `vista_indice_comercio`, `vista_indice_sucursal` | P3 y decisión en SQL; el análisis verifica que coincidan con Pandas |
| Clases | `ConexionBD` | Conexión (PyMySQL) y `crear_engine` (SQLAlchemy para Pandas) |
| | `ProductoCRUD` | Búsquedas y consulta de la vista desde el menú |
| | `Producto`, `Sucursal`, `Precio` | Entidades que muestra el menú |
| Pandas | `read_sql`, `groupby` + `transform` (size, mean, median), filtros booleanos, `agg`, `merge`, `rank`, `describe` | Comparables, P1, P2, P3 |
| NumPy | `percentile`, `median`, `mean`, `std`, comparaciones vectorizadas | Indicadores, distribución de la variación, valores extremos |

## Alcances

- Datos de abril–mayo de 2020: no usar como precios actuales.
- Las 40 sucursales con precios no cubren todas las localidades; un
  comercio con una sola sucursal (Mariano, Dinosaurio, Millán) refleja
  esa sucursal, no la cadena.
- El índice se calcula contra el promedio del producto entre las
  sucursales del dataset, no contra un precio de referencia oficial.
