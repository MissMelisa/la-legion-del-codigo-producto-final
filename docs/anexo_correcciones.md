# Anexo: correcciones a partir de la devolución de la Evidencia 3

## Obligatorios (afectan los números presentados)

| # | Observación | Corrección | Dónde |
|---|---|---|---|
| 1 | Cifras divergentes dentro del informe (p. ej. promedio por comercio). | Todas las cifras salen de un solo script que lee MySQL y escribe `resultados/resumen.md`. El informe y el póster citan solo ese archivo. Además, el análisis verifica que el índice de Pandas coincida con la vista SQL. | `app/analisis.py`, `resultados/resumen.md` |
| 2 | El análisis agrupaba por **nombre** de producto. | Se agrupa por `producto_id` (código de barras). Hay 960 nombres compartidos por dos o más códigos distintos: al agrupar por nombre se mezclaban precios de productos diferentes. | `app/analisis.py`, `vista_resumen_producto` |
| 3 | P1: hay que elegir una tabla final de productos equivalentes con ejemplos numéricos concretos. | Se define "producto comparable" (mismo código, con precio en 10 o más sucursales: 2.841 productos). La tabla final es una canasta de los 10 productos con más sucursales, con mínimo, comercio del mínimo, máximo y comercio del máximo. Los empates se informan. | `resultados/resumen.md` (P1), `vista_precio_minimo_producto` |
| 4 | P2: el ranking de 20 productos no da un valor que resuma todos los casos. | Se resume con la distribución de la variación sobre los productos comparables: mediana 42,2 %, rango intercuartil 28,8–60,5 %, % de productos con variación > 25 % y > 50 %, e histograma. | `resultados/resumen.md` (P2), `g1_variacion_por_producto.png` |
| 5 | P3: comparar promedios de comercios con surtidos diferentes no prueba cuál es más económico (Dinosaurio "más caro", Pan American Energy "más barato"). | Se reemplaza por un índice relativo (precio ÷ promedio del mismo producto) sobre productos comparables, con un mínimo de 100 productos por comercio. El orden se invierte: Dinosaurio pasa a −8,6 % y Pan American Energy queda sin muestra suficiente (12 productos). | `app/analisis.py`, `vista_indice_comercio`, `g2_promedio_vs_indice_comercio.png` |
| 6 | El mínimo ($2,69) y el máximo ($19.500) generales son de productos distintos. | Se presentan con el nombre del producto y una aclaración de que no son una diferencia de un mismo producto. | `resultados/resumen.md` (Indicadores generales) |
| 7 | Contrastar valores extremos. | Se marcan los precios a más de 3 veces (o a menos de 1/3) de la mediana de su producto: 51 precios, que afectan a 6 productos comparables. Se exportan y se señalan como "a contrastar" en el ranking de P2. | `resultados/valores_extremos.csv` |
| 8 | La instalación limpia no estaba verificada: `fullscript.sql` usaba `ADD COLUMN IF NOT EXISTS` (no existe en MySQL) y no cargaba datos. | Script único `sql/datos_comercios.sql`: crea la base, las tablas, carga los datos y crea 6 vistas. Probado sin errores en MySQL 9.6 sobre una base vacía. Las columnas calculadas en `productos` se reemplazan por vistas (no se guardan datos derivados). | `sql/datos_comercios.sql`, `preparacion/generar_sql.py` |
| 9 | Falta un punto de entrada y un LÉAME con pasos verificables. | `main.py` abre el menú. El LÉAME describe requirements, `.env`, carga de la base y ejecución. La instalación se probó desde un entorno virtual nuevo. | `main.py`, `README.md` |
| 10 | Credenciales en el repositorio (`docker-compose.yml` con contraseñas). El análisis no leía `.env` y fallaba con contraseñas con caracteres especiales. | Se elimina `docker-compose.yml`. La conexión se lee solo de `.env` (no versionado), con `.env.ejemplo` como plantilla. La contraseña se codifica en la URL. | `app/conexion.py`, `.env.ejemplo`, `.gitignore` |

## Mejoras sugeridas incorporadas

| Mejora | Cómo |
|---|---|
| Normalizar localidades | Se unifican las variantes de escritura ("CORDOBA", "Capital", "Córdoba", "CIUDAD DE CORDOBA NORTE"…): de 66 formas de escribir las localidades se pasa a 42 localidades. |
| Análisis por sucursal y localidad | Índice por sucursal con su localidad: identifica las sucursales relativamente más caras, base de la decisión de gestión (`indice_por_sucursal.csv`, `g3_indice_por_sucursal.png`). |
| Restricción de precio válido en la base | `CHECK (precio > 0)` en la tabla `precios`. |
| Base más liviana | Se cargan solo los productos con precio en Córdoba (22.565 de 72.038). |
| Estructura del código | Paquete `app/` con imports explícitos (sin modificar `sys.path`). Se eliminan los scripts que ya no se usan (`load-to-mysql.py`, `populate-categories.py`, `update-columns.py`). |

## Sin cambios

- 99.681 registros de precio (un precio por producto y sucursal, el del
  archivo semanal más reciente), igual que en la Evidencia 3.
- Indicadores generales: promedio $166,68, mediana $110,00, desvío $247,99.
