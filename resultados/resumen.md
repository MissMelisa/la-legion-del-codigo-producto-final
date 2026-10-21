# Resultados del análisis

> Archivo generado por `python -m app.analisis`. Es la única fuente de
> cifras para el informe y el póster: si se vuelve a cargar la base,
> se regenera y los números quedan consistentes.

Datos: Precios Claros (SEPA), sucursales de Córdoba, abril-mayo de 2020
(muestra histórica: no son precios vigentes).

## Indicadores generales

| Indicador | Valor |
|---|---|
| Registros de precio (producto + sucursal) | 99.681 |
| Productos distintos | 22.565 |
| Sucursales con precios | 40 |
| Comercios (razón social) | 12 |
| Promedio general | $166,68 |
| Mediana | $110,00 |
| Rango intercuartil (P25 – P75) | $64,90 – $196,95 |
| Desvío estándar | $247,99 |
| Mínimo general | $2,69 (Cubanito Chocolate Oblita 5 Gr) |
| Máximo general | $19.500,00 (Champagne Estuche Dom Perignon 750 Ml) |

El mínimo y el máximo generales corresponden a **productos distintos**:
no representan la diferencia de precio de un mismo producto.

## Criterio de productos comparables

Se comparan precios del **mismo producto** (mismo `producto_id`, es decir
mismo código de barras) entre sucursales. Se consideran comparables los
productos con precio en al menos **10 sucursales**:
2.841 productos.

Valores extremos a contrastar: 51 precios están a más de
3 veces (o a menos de 1/3) de la mediana de su producto
(`resultados/valores_extremos.csv`). Se conservan, pero se señalan en
las tablas, porque pueden ser errores de carga o presentaciones distintas
con el mismo código.

## P1. Precio mínimo de cada producto y comercio donde se encuentra

Canasta de ejemplo: los 10 productos con precio en más sucursales.

| producto | sucursales | precio_minimo | comercio_minimo | precio_maximo | comercio_maximo | diferencia | variacion_pct |
|---|---|---|---|---|---|---|---|
| Cerveza Rubia Retornable Schneider 1 Lt | 32 | $54,99 | Cyre S.A. | $116,00 | INC S.A., Libertad S.A | $61,01 | 110,9 % |
| Aceite de Girasol Natura 1.5 Lt | 30 | $126,00 | Dinosaurio S.A. | $185,00 | INC S.A., Libertad S.A | $59,00 | 46,8 % |
| Agua Mineral sin Gas Villavicencio 2 Lt | 30 | $39,90 | Miguel Becerra S.A. | $81,90 | Millan S.A. | $42,00 | 105,3 % |
| Agua Saborizada Pera sin Gas Aquarius 1.5 Lt | 30 | $43,99 | DIA Argentina S.A | $85,00 | Jumbo Retail Argentina S.A., Millan S.A. | $41,01 | 93,2 % |
| Agua Saborizada Pera sin Gas Aquarius 2.25 Lt | 30 | $53,89 | DIA Argentina S.A | $110,00 | Libertad S.A | $56,11 | 104,1 % |
| Cafe Instantaneo Suave NesCafe Dolca 170 Gr | 30 | $199,00 | INC S.A. | $379,00 | Jumbo Retail Argentina S.A. | $180,00 | 90,5 % |
| Cerveza Rubia Retornable Heineken 1 Lt | 30 | $89,00 | Miguel Becerra S.A. | $171,00 | INC S.A., Libertad S.A | $82,00 | 92,1 % |
| Sal Fina en Estuche Dos Anclas 500 Gr | 30 | $25,90 | S.A. Importadora y Exportadora de la Patagonia | $44,00 | Jumbo Retail Argentina S.A., S.A. Importadora y Exportadora de la Patagonia | $18,10 | 69,9 % |
| Cafe Suave Doypack Dolca 170 Gr | 29 | $149,99 | Libertad S.A | $281,00 | INC S.A., Libertad S.A | $131,01 | 87,3 % |
| Coca Cola Retornable 2 Lt | 29 | $73,25 | DIA Argentina S.A | $90,00 | Jumbo Retail Argentina S.A. | $16,75 | 22,9 % |

Cantidad de productos comparables en los que cada comercio tiene el
precio más bajo (los empates cuentan para cada comercio):

| comercio | productos_con_precio_minimo | productos_presentes | pct_de_sus_productos | pct_del_total |
|---|---|---|---|---|
| Miguel Becerra S.A. | 736 | 1925 | 38,2 % | 25,9 % |
| Dinosaurio S.A. | 553 | 1736 | 31,9 % | 19,5 % |
| Cyre S.A. | 465 | 2029 | 22,9 % | 16,4 % |
| INC S.A. | 416 | 2584 | 16,1 % | 14,6 % |
| Jumbo Retail Argentina S.A. | 247 | 1877 | 13,2 % | 8,7 % |
| Libertad S.A | 205 | 1921 | 10,7 % | 7,2 % |
| Wal Mart Argentina S.R.L. | 110 | 2037 | 5,4 % | 3,9 % |
| Mariano S.A. | 108 | 468 | 23,1 % | 3,8 % |
| S.A. Importadora y Exportadora de la Patagonia | 76 | 421 | 18,1 % | 2,7 % |
| Millan S.A. | 71 | 555 | 12,8 % | 2,5 % |
| DIA Argentina S.A | 33 | 84 | 39,3 % | 1,2 % |
| Pan American Energy LLC Argentina | 1 | 12 | 8,3 % | 0,0 % |

Tabla completa: `resultados/p1_precio_minimo_por_producto.csv`.

## P2. Diferencia entre el precio máximo y mínimo de cada producto

| Indicador (sobre 2.841 productos comparables) | Valor |
|---|---|
| Variación máx–mín mediana | **42,2 %** |
| Rango intercuartil de la variación | 28,8 % – 60,5 % |
| Percentil 90 | 82,3 % |
| Productos con variación > 25 % | 82,0 % |
| Productos con variación > 50 % | 36,9 % |
| Diferencia máx–mín mediana en pesos | $34,31 |
| Productos con algún valor extremo a contrastar | 6 |

Los 10 productos comparables con mayor variación porcentual:

| producto | sucursales | precio_minimo | precio_maximo | variacion_pct | a_contrastar |
|---|---|---|---|---|---|
| Gaseosa Tonica Schweppes 1.5 Lt | 20 | $13,65 | $155,00 | 1.035,5 % | sí |
| Cerveza Rubia Miller 473 Cc | 11 | $80,00 | $477,00 | 496,3 % | sí |
| Palitos para Brochette Ideal 25 Un | 14 | $28,60 | $139,00 | 386,0 % | sí |
| Sopa de Arvejas Knorr Quick 5 Un | 18 | $33,90 | $139,00 | 310,0 % | sí |
| Agua Saborizada Manzana sin Gas Aquarius 2.25 Lt | 15 | $26,99 | $107,00 | 296,4 % | sí |
| Pure de Tomate Tetrabrik Salsati La Campagnola 520 Gr | 24 | $17,90 | $65,68 | 266,9 % | sí |
| Arroz Doble Carolina Dos Hermanos 1 Kg | 16 | $44,99 | $149,67 | 232,7 % | no |
| Coca Cola sin Azucar 1.5 Lt | 23 | $48,99 | $155,00 | 216,4 % | no |
| Lavavajilla Ultra Limon Ala 300 Cc | 19 | $24,59 | $77,50 | 215,2 % | no |
| Jabon de Tocador Renovacion Diaria Plusbelle 375 Gr | 14 | $52,00 | $159,00 | 205,8 % | no |

Gráfico: `resultados/g1_variacion_por_producto.png`.

## P3. Precio de los productos según cada comercio

El promedio simple por comercio compara surtidos distintos (un comercio
con muchos productos caros sale "caro" aunque cobre menos por los mismos
productos). Por eso se usa un **índice relativo**: cada precio se divide
por el precio promedio de ese mismo producto entre todas las sucursales,
y se promedia por comercio. 0 % = precio promedio; +5 % = 5 % más caro.
En las columnas de puesto, 1 = el más caro según ese criterio.

| comercio | promedio_simple | puesto_promedio_simple | indice | puesto_indice | productos_comparados | muestra |
|---|---|---|---|---|---|---|
| DIA Argentina S.A | $80,65 | 11 | -20,7 % | 12 | 84 | insuficiente |
| Mariano S.A. | $121,43 | 10 | -10,0 % | 11 | 468 | suficiente |
| Miguel Becerra S.A. | $134,18 | 7 | -9,8 % | 10 | 1925 | suficiente |
| Dinosaurio S.A. | $223,62 | 1 | -8,6 % | 9 | 1736 | suficiente |
| Millan S.A. | $129,30 | 9 | -2,5 % | 8 | 555 | suficiente |
| INC S.A. | $169,36 | 3 | +0,1 % | 7 | 2584 | suficiente |
| Cyre S.A. | $131,15 | 8 | +2,4 % | 6 | 2029 | suficiente |
| S.A. Importadora y Exportadora de la Patagonia | $142,02 | 6 | +2,4 % | 5 | 421 | suficiente |
| Wal Mart Argentina S.R.L. | $165,76 | 4 | +2,5 % | 4 | 2037 | suficiente |
| Libertad S.A | $152,96 | 5 | +4,3 % | 3 | 1921 | suficiente |
| Jumbo Retail Argentina S.A. | $205,83 | 2 | +5,2 % | 2 | 1877 | suficiente |
| Pan American Energy LLC Argentina | $71,69 | 12 | +46,1 % | 1 | 12 | insuficiente |

Con muestra suficiente (100 o más productos comparables), el comercio
relativamente más barato es **Mariano S.A.**
(-10,0 %) y el más caro es
**Jumbo Retail Argentina S.A.** (+5,2 %).

Control de consistencia: el índice calculado con Pandas coincide con la
vista SQL `vista_indice_comercio` (diferencia máxima 0.000042).

Gráfico: `resultados/g2_promedio_vs_indice_comercio.png`.

## Insumo para la decisión de gestión

Sucursales relativamente más caras sobre productos comparables
(candidatas a revisar precios o evaluar promociones):

| bandera_descripcion | sucursal_nombre | localidad | comercio | productos_comparados | indice |
|---|---|---|---|---|---|
| Disco | SM 583 - Villa Allende. | Villa Allende | Jumbo Retail Argentina S.A. | 1616 | +9,8 % |
| Mini Libertad | Mini Ambrosio Olmos | Córdoba | Libertad S.A | 894 | +8,9 % |
| Supermercados Cordiez | Cordiez 47 | Capilla del Monte | Cyre S.A. | 1093 | +8,7 % |
| Mini Libertad | Mini Libertad Octavio Pinto | Córdoba | Libertad S.A | 757 | +8,6 % |
| Express | 25 de Mayo 979 | Córdoba | INC S.A. | 1331 | +8,2 % |

Ranking completo: `resultados/indice_por_sucursal.csv`.
Gráfico: `resultados/g3_indice_por_sucursal.png`.
