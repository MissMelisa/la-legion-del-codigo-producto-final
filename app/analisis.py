"""
Análisis de precios con Pandas y NumPy, leyendo los datos desde MySQL.

Responde la pregunta central del recorte:

    ¿Qué diferencias de precio presenta un mismo producto entre
    sucursales de Córdoba y cómo pueden usarse para orientar
    decisiones comerciales?

a partir de tres preguntas de la Evidencia 1:

    P1. Precio mínimo de cada producto y comercio donde se encuentra.
    P2. Diferencia entre el precio máximo y mínimo de cada producto.
    P3. Precio de los productos según cada comercio (índice relativo
        sobre productos comparables, en lugar del promedio simple).

Todas las cifras que van al informe y al póster salen de este script
y se guardan en resultados/ (resumen.md + CSV + gráficos), para que
haya una única fuente de números.

Uso (desde la raíz del proyecto):
    python -m app.analisis
    python -m app.analisis --sin-graficos
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from app.conexion import crear_engine


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTADOS_DIR = BASE_DIR / "resultados"

# Un producto es "comparable" si tiene precio en al menos esta cantidad
# de sucursales. Debe coincidir con MIN_SUCURSALES de
# preparacion/generar_sql.py (vistas vista_indice_*).
MIN_SUCURSALES = 10

# Mínimo de productos comparables distintos para que el índice de un
# comercio o sucursal se considere representativo.
MIN_PRODUCTOS = 100

# Un precio se marca como valor extremo a contrastar si está a más de
# este factor (por arriba o por abajo) de la mediana de su producto.
FACTOR_EXTREMO = 3

COLOR_SERIE = "#2a78d6"
COLOR_REFERENCIA = "#898781"
COLOR_TEXTO = "#3d3c38"
COLOR_FONDO = "#fcfcfb"


# ==========================================
# Carga
# ==========================================

def cargar_datos():
    """Lee vista_precios_detalle desde MySQL a un DataFrame."""
    consulta = """
        SELECT producto_id, producto, marca, presentacion, categoria_1,
               precio, sucursal_id, sucursal_nombre, bandera_descripcion,
               comercio_razon_social AS comercio, localidad
        FROM vista_precios_detalle
    """
    df = pd.read_sql(consulta, crear_engine())
    df["precio"] = df["precio"].astype(float)
    return df


def leer_vista(nombre):
    return pd.read_sql(f"SELECT * FROM {nombre}", crear_engine())


# ==========================================
# Preparación
# ==========================================

def marcar_comparables(df):
    """Agrega por producto: cantidad de sucursales, mediana, promedio,
    índice relativo y marca de valor extremo."""
    por_producto = df.groupby("producto_id")["precio"]
    df = df.assign(
        sucursales_producto=por_producto.transform("size"),
        mediana_producto=por_producto.transform("median"),
        promedio_producto=por_producto.transform("mean"),
    )
    df["comparable"] = df["sucursales_producto"] >= MIN_SUCURSALES
    df["indice"] = df["precio"] / df["promedio_producto"]

    razon = df["precio"].to_numpy() / df["mediana_producto"].to_numpy()
    df["extremo"] = (razon > FACTOR_EXTREMO) | (razon < 1 / FACTOR_EXTREMO)
    return df


# ==========================================
# Estadística descriptiva
# ==========================================

def estadisticas_generales(df):
    precios = df["precio"].to_numpy()
    q1, mediana, q3 = np.percentile(precios, [25, 50, 75])
    return {
        "registros": len(df),
        "productos": df["producto_id"].nunique(),
        "sucursales": df["sucursal_id"].nunique(),
        "comercios": df["comercio"].nunique(),
        "promedio": float(np.mean(precios)),
        "mediana": float(mediana),
        "q1": float(q1),
        "q3": float(q3),
        "desvio": float(np.std(precios, ddof=1)),
        "minimo": float(np.min(precios)),
        "maximo": float(np.max(precios)),
        "producto_minimo": df.loc[df["precio"].idxmin(), "producto"],
        "producto_maximo": df.loc[df["precio"].idxmax(), "producto"],
    }


# ==========================================
# P1: precio mínimo por producto y comercio
# ==========================================

def precio_minimo(comparables):
    """Una fila por producto comparable: mínimo, comercio(s) donde se
    encuentra, máximo y comercio(s) donde se encuentra."""

    def comercios_con(grupo, valor):
        return ", ".join(sorted(grupo.loc[grupo["precio"] == valor, "comercio"].unique()))

    filas = []
    for producto_id, grupo in comparables.groupby("producto_id"):
        minimo = grupo["precio"].min()
        maximo = grupo["precio"].max()
        filas.append({
            "producto_id": producto_id,
            "producto": grupo["producto"].iat[0],
            "sucursales": len(grupo),
            "precio_minimo": minimo,
            "comercio_minimo": comercios_con(grupo, minimo),
            "precio_maximo": maximo,
            "comercio_maximo": comercios_con(grupo, maximo),
            "diferencia": round(maximo - minimo, 2),
            "variacion_pct": round((maximo - minimo) / minimo * 100, 1),
            "tiene_extremos": bool(grupo["extremo"].any()),
        })
    return pd.DataFrame(filas)


def minimos_por_comercio(comparables, total_productos):
    """En cuántos productos comparables cada comercio tiene el precio
    más bajo (un empate cuenta para todos los comercios empatados)."""
    en_minimo = comparables[
        comparables["precio"] == comparables.groupby("producto_id")["precio"].transform("min")
    ]
    conteo = (
        en_minimo.groupby("comercio")["producto_id"].nunique()
        .rename("productos_con_precio_minimo")
    )
    presentes = comparables.groupby("comercio")["producto_id"].nunique().rename("productos_presentes")
    tabla = pd.concat([conteo, presentes], axis=1).fillna(0).astype(int)
    tabla["pct_de_sus_productos"] = (
        tabla["productos_con_precio_minimo"] / tabla["productos_presentes"] * 100
    ).round(1)
    tabla["pct_del_total"] = (
        tabla["productos_con_precio_minimo"] / total_productos * 100
    ).round(1)
    tabla.index.name = "comercio"
    return tabla.sort_values("productos_con_precio_minimo", ascending=False)


# ==========================================
# P2: diferencia máximo - mínimo
# ==========================================

def resumen_variacion(tabla_productos):
    variacion = tabla_productos["variacion_pct"].to_numpy()
    p25, mediana, p75, p90 = np.percentile(variacion, [25, 50, 75, 90])
    return {
        "productos": len(variacion),
        "mediana": float(mediana),
        "p25": float(p25),
        "p75": float(p75),
        "p90": float(p90),
        "pct_mayor_25": float(np.mean(variacion > 25) * 100),
        "pct_mayor_50": float(np.mean(variacion > 50) * 100),
        "diferencia_mediana": float(np.median(tabla_productos["diferencia"])),
        "con_extremos": int(tabla_productos["tiene_extremos"].sum()),
    }


# ==========================================
# P3: precio según comercio
# ==========================================

def indice_por(comparables, columnas):
    tabla = (
        comparables.groupby(columnas)
        .agg(
            sucursales=("sucursal_id", "nunique"),
            productos_comparados=("producto_id", "nunique"),
            precios_comparados=("indice", "size"),
            indice_promedio=("indice", "mean"),
        )
        .reset_index()
    )
    tabla["representativo"] = tabla["productos_comparados"] >= MIN_PRODUCTOS
    return tabla.sort_values("indice_promedio")


def comparar_promedio_e_indice(df, comparables):
    simple = (
        df.groupby("comercio")
        .agg(precios=("precio", "size"), promedio_simple=("precio", "mean"))
        .reset_index()
    )
    # Puesto 1 = más caro, en ambos criterios
    simple["puesto_promedio_simple"] = simple["promedio_simple"].rank(ascending=False).astype(int)
    indice = indice_por(comparables, ["comercio"])
    indice["puesto_indice"] = indice["indice_promedio"].rank(ascending=False).astype(int)
    return simple.merge(indice, on="comercio", how="left").sort_values("indice_promedio")


def verificar_contra_sql(indice_comercio):
    """Control de consistencia: el índice calculado en Pandas debe
    coincidir con la vista SQL vista_indice_comercio."""
    sql = leer_vista("vista_indice_comercio").set_index("comercio")
    pandas = indice_comercio.set_index("comercio")["indice_promedio"]
    diferencia = (pandas - sql["indice_promedio"].astype(float)).abs().max()
    if diferencia > 1e-3:
        raise AssertionError(
            f"El índice de Pandas y el de la vista SQL difieren ({diferencia:.4f})"
        )
    return diferencia


# ==========================================
# Gráficos
# ==========================================

def _ejes(ax):
    ax.set_facecolor(COLOR_FONDO)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(COLOR_REFERENCIA)
    ax.tick_params(colors=COLOR_TEXTO, labelsize=9)
    ax.grid(axis="x", color="#e6e4df", linewidth=0.8)
    ax.set_axisbelow(True)


def _etiquetar_barras(ax, y, valores):
    for yi, valor in zip(y, valores):
        ax.annotate(f"{valor:+.1f} %", xy=(valor, yi), xytext=(4 if valor >= 0 else -4, 0),
                    textcoords="offset points", va="center",
                    ha="left" if valor >= 0 else "right", fontsize=8, color=COLOR_TEXTO)


def graficar(tabla_productos, comparacion, indice_sucursal, variacion):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 1. Distribución de la variación máx-mín por producto
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=COLOR_FONDO)
    _ejes(ax)
    ax.grid(axis="y", color="#e6e4df", linewidth=0.8)
    ax.grid(axis="x", visible=False)
    valores = np.clip(tabla_productos["variacion_pct"], 0, 200)
    ax.hist(valores, bins=np.arange(0, 205, 5), color=COLOR_SERIE,
            edgecolor=COLOR_FONDO, linewidth=1)
    ax.axvline(variacion["mediana"], color=COLOR_TEXTO, linewidth=1.5, linestyle="--")
    ax.annotate(f"mediana {variacion['mediana']:.0f} %",
                xy=(variacion["mediana"], ax.get_ylim()[1] * 0.92),
                xytext=(6, 0), textcoords="offset points", fontsize=9, color=COLOR_TEXTO)
    ax.set_xlabel("Variación entre precio máximo y mínimo del mismo producto (%; 200 o más en la última barra)")
    ax.set_ylabel("Productos")
    ax.set_title(
        "Diferencia de precio de un mismo producto entre sucursales\n"
        f"{len(tabla_productos)} productos con precio en {MIN_SUCURSALES} o más sucursales",
        fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(RESULTADOS_DIR / "g1_variacion_por_producto.png", dpi=150)
    plt.close(fig)

    # 2. Promedio simple vs índice relativo por comercio (dos paneles
    #    con la misma fila por comercio; nunca dos escalas en un eje)
    datos = comparacion[comparacion["representativo"]].sort_values("indice_promedio", ascending=False)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True, facecolor=COLOR_FONDO)
    for ax in (ax1, ax2):
        _ejes(ax)
    y = np.arange(len(datos))
    ax1.barh(y, datos["promedio_simple"], color=COLOR_REFERENCIA, height=0.6)
    ax1.set_yticks(y, datos["comercio"])
    ax1.set_title("Promedio simple ($)\nmezcla surtidos distintos", fontsize=10, loc="left")
    for yi, valor in zip(y, datos["promedio_simple"]):
        ax1.annotate(f"${valor:.0f}", xy=(valor, yi), xytext=(4, 0), textcoords="offset points",
                     va="center", fontsize=8, color=COLOR_TEXTO)
    pct = (datos["indice_promedio"] - 1) * 100
    ax2.barh(y, pct, color=COLOR_SERIE, height=0.6)
    ax2.axvline(0, color=COLOR_TEXTO, linewidth=1)
    ax2.set_xlim(pct.min() - 8, pct.max() + 6)
    ax2.set_title("Índice sobre productos comparables\n% respecto del precio promedio del mismo producto",
                  fontsize=10, loc="left")
    _etiquetar_barras(ax2, y, pct)
    fig.suptitle("El promedio simple ordena distinto que la comparación de un mismo producto",
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(RESULTADOS_DIR / "g2_promedio_vs_indice_comercio.png", dpi=150)
    plt.close(fig)

    # 3. Sucursales más caras y más baratas (índice)
    representativas = indice_sucursal[indice_sucursal["representativo"]].sort_values("indice_promedio")
    extremos = pd.concat([representativas.head(8), representativas.tail(8)])
    etiquetas = (extremos["bandera_descripcion"] + " · " + extremos["sucursal_nombre"]
                 + " (" + extremos["localidad"] + ")")
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLOR_FONDO)
    _ejes(ax)
    y = np.arange(len(extremos))
    pct = (extremos["indice_promedio"] - 1) * 100
    ax.barh(y, pct, color=COLOR_SERIE, height=0.6)
    ax.axvline(0, color=COLOR_TEXTO, linewidth=1)
    ax.set_xlim(pct.min() - 5, pct.max() + 5)
    ax.set_yticks(y, etiquetas, fontsize=8)
    _etiquetar_barras(ax, y, pct)
    ax.set_xlabel("% respecto del precio promedio del mismo producto")
    ax.set_title("Las 8 sucursales relativamente más baratas y las 8 más caras\n"
                 f"(sucursales con {MIN_PRODUCTOS} o más productos comparables)",
                 fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(RESULTADOS_DIR / "g3_indice_por_sucursal.png", dpi=150)
    plt.close(fig)


# ==========================================
# Informe de resultados
# ==========================================

def pesos(valor):
    texto = f"{valor:,.2f}"
    return "$" + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor, decimales=1):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def porcentaje_indice(indice):
    return f"{(indice - 1) * 100:+.1f} %".replace(".", ",")


def tabla_md(df):
    columnas = list(df.columns)
    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for fila in df.itertuples(index=False):
        lineas.append("| " + " | ".join(str(v) for v in fila) + " |")
    return "\n".join(lineas)


def escribir_resumen(generales, n_comparables, variacion, canasta, ranking_variacion,
                     minimos_comercio, comparacion, indice_sucursal, extremos, dif_sql):
    canasta_md = canasta.assign(
        precio_minimo=canasta["precio_minimo"].map(pesos),
        precio_maximo=canasta["precio_maximo"].map(pesos),
        diferencia=canasta["diferencia"].map(pesos),
        variacion_pct=canasta["variacion_pct"].map(lambda v: numero(v) + " %"),
    )[["producto", "sucursales", "precio_minimo", "comercio_minimo",
       "precio_maximo", "comercio_maximo", "diferencia", "variacion_pct"]]

    ranking_md = ranking_variacion.assign(
        precio_minimo=ranking_variacion["precio_minimo"].map(pesos),
        precio_maximo=ranking_variacion["precio_maximo"].map(pesos),
        variacion_pct=ranking_variacion["variacion_pct"].map(lambda v: numero(v) + " %"),
        a_contrastar=ranking_variacion["tiene_extremos"].map({True: "sí", False: "no"}),
    )[["producto", "sucursales", "precio_minimo", "precio_maximo", "variacion_pct", "a_contrastar"]]

    comparacion_md = comparacion.assign(
        promedio_simple=comparacion["promedio_simple"].map(pesos),
        indice=comparacion["indice_promedio"].map(porcentaje_indice),
        muestra=comparacion["representativo"].map({True: "suficiente", False: "insuficiente"}),
    )[["comercio", "promedio_simple", "puesto_promedio_simple", "indice",
       "puesto_indice", "productos_comparados", "muestra"]]

    minimos_md = minimos_comercio.reset_index()
    for columna in ("pct_de_sus_productos", "pct_del_total"):
        minimos_md[columna] = minimos_md[columna].map(lambda v: numero(v) + " %")

    representativas = indice_sucursal[indice_sucursal["representativo"]]
    caras = representativas.sort_values("indice_promedio", ascending=False).head(5)
    caras_md = caras.assign(
        indice=caras["indice_promedio"].map(porcentaje_indice),
    )[["bandera_descripcion", "sucursal_nombre", "localidad", "comercio", "productos_comparados", "indice"]]

    con_muestra = comparacion[comparacion["representativo"]]
    mas_barato = con_muestra.iloc[0]
    mas_caro = con_muestra.iloc[-1]

    texto = f"""# Resultados del análisis

> Archivo generado por `python -m app.analisis`. Es la única fuente de
> cifras para el informe y el póster: si se vuelve a cargar la base,
> se regenera y los números quedan consistentes.

Datos: Precios Claros (SEPA), sucursales de Córdoba, abril-mayo de 2020
(muestra histórica: no son precios vigentes).

## Indicadores generales

| Indicador | Valor |
|---|---|
| Registros de precio (producto + sucursal) | {numero(generales['registros'], 0)} |
| Productos distintos | {numero(generales['productos'], 0)} |
| Sucursales con precios | {generales['sucursales']} |
| Comercios (razón social) | {generales['comercios']} |
| Promedio general | {pesos(generales['promedio'])} |
| Mediana | {pesos(generales['mediana'])} |
| Rango intercuartil (P25 – P75) | {pesos(generales['q1'])} – {pesos(generales['q3'])} |
| Desvío estándar | {pesos(generales['desvio'])} |
| Mínimo general | {pesos(generales['minimo'])} ({generales['producto_minimo']}) |
| Máximo general | {pesos(generales['maximo'])} ({generales['producto_maximo']}) |

El mínimo y el máximo generales corresponden a **productos distintos**:
no representan la diferencia de precio de un mismo producto.

## Criterio de productos comparables

Se comparan precios del **mismo producto** (mismo `producto_id`, es decir
mismo código de barras) entre sucursales. Se consideran comparables los
productos con precio en al menos **{MIN_SUCURSALES} sucursales**:
{numero(n_comparables, 0)} productos.

Valores extremos a contrastar: {numero(len(extremos), 0)} precios están a más de
{FACTOR_EXTREMO} veces (o a menos de 1/{FACTOR_EXTREMO}) de la mediana de su producto
(`resultados/valores_extremos.csv`). Se conservan, pero se señalan en
las tablas, porque pueden ser errores de carga o presentaciones distintas
con el mismo código.

## P1. Precio mínimo de cada producto y comercio donde se encuentra

Canasta de ejemplo: los 10 productos con precio en más sucursales.

{tabla_md(canasta_md)}

Cantidad de productos comparables en los que cada comercio tiene el
precio más bajo (los empates cuentan para cada comercio):

{tabla_md(minimos_md)}

Tabla completa: `resultados/p1_precio_minimo_por_producto.csv`.

## P2. Diferencia entre el precio máximo y mínimo de cada producto

| Indicador (sobre {numero(variacion['productos'], 0)} productos comparables) | Valor |
|---|---|
| Variación máx–mín mediana | **{numero(variacion['mediana'])} %** |
| Rango intercuartil de la variación | {numero(variacion['p25'])} % – {numero(variacion['p75'])} % |
| Percentil 90 | {numero(variacion['p90'])} % |
| Productos con variación > 25 % | {numero(variacion['pct_mayor_25'])} % |
| Productos con variación > 50 % | {numero(variacion['pct_mayor_50'])} % |
| Diferencia máx–mín mediana en pesos | {pesos(variacion['diferencia_mediana'])} |
| Productos con algún valor extremo a contrastar | {variacion['con_extremos']} |

Los 10 productos comparables con mayor variación porcentual:

{tabla_md(ranking_md)}

Gráfico: `resultados/g1_variacion_por_producto.png`.

## P3. Precio de los productos según cada comercio

El promedio simple por comercio compara surtidos distintos (un comercio
con muchos productos caros sale "caro" aunque cobre menos por los mismos
productos). Por eso se usa un **índice relativo**: cada precio se divide
por el precio promedio de ese mismo producto entre todas las sucursales,
y se promedia por comercio. 0 % = precio promedio; +5 % = 5 % más caro.
En las columnas de puesto, 1 = el más caro según ese criterio.

{tabla_md(comparacion_md)}

Con muestra suficiente ({MIN_PRODUCTOS} o más productos comparables), el comercio
relativamente más barato es **{mas_barato['comercio']}**
({porcentaje_indice(mas_barato['indice_promedio'])}) y el más caro es
**{mas_caro['comercio']}** ({porcentaje_indice(mas_caro['indice_promedio'])}).

Control de consistencia: el índice calculado con Pandas coincide con la
vista SQL `vista_indice_comercio` (diferencia máxima {dif_sql:.6f}).

Gráfico: `resultados/g2_promedio_vs_indice_comercio.png`.

## Insumo para la decisión de gestión

Sucursales relativamente más caras sobre productos comparables
(candidatas a revisar precios o evaluar promociones):

{tabla_md(caras_md)}

Ranking completo: `resultados/indice_por_sucursal.csv`.
Gráfico: `resultados/g3_indice_por_sucursal.png`.
"""
    (RESULTADOS_DIR / "resumen.md").write_text(texto, encoding="utf-8")


# ==========================================
# MAIN
# ==========================================

def main(graficos=True):
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 12)
    RESULTADOS_DIR.mkdir(exist_ok=True)

    print("Leyendo vista_precios_detalle desde MySQL...")
    df = marcar_comparables(cargar_datos())

    generales = estadisticas_generales(df)
    print("\n===== ESTADÍSTICAS DESCRIPTIVAS DE PRECIOS =====")
    print(df["precio"].describe().round(2))

    comparables = df[df["comparable"]]
    n_comparables = comparables["producto_id"].nunique()
    print(f"\nProductos comparables ({MIN_SUCURSALES} o más sucursales): {n_comparables}")

    extremos = df[df["extremo"]].sort_values("producto_id")
    extremos[["producto_id", "producto", "presentacion", "precio", "mediana_producto",
              "sucursal_nombre", "comercio"]].to_csv(
        RESULTADOS_DIR / "valores_extremos.csv", index=False)

    # P1
    tabla_productos = precio_minimo(comparables)
    tabla_productos.sort_values("producto").to_csv(
        RESULTADOS_DIR / "p1_precio_minimo_por_producto.csv", index=False)
    canasta = tabla_productos.sort_values(["sucursales", "producto"], ascending=[False, True]).head(10)
    minimos_comercio = minimos_por_comercio(comparables, n_comparables)
    print("\n===== P1. PRECIO MÍNIMO POR PRODUCTO (canasta de ejemplo) =====")
    print(canasta[["producto", "sucursales", "precio_minimo", "comercio_minimo"]].to_string(index=False))
    print("\nProductos en los que cada comercio tiene el precio mínimo:")
    print(minimos_comercio)

    # P2
    variacion = resumen_variacion(tabla_productos)
    ranking_variacion = tabla_productos.sort_values("variacion_pct", ascending=False).head(10)
    tabla_productos.sort_values("variacion_pct", ascending=False).to_csv(
        RESULTADOS_DIR / "p2_diferencia_por_producto.csv", index=False)
    print("\n===== P2. DIFERENCIA MÁXIMO - MÍNIMO =====")
    print(f"Variación mediana: {variacion['mediana']:.1f} % "
          f"(P25 {variacion['p25']:.1f} % - P75 {variacion['p75']:.1f} %)")
    print(f"Productos con variación > 50 %: {variacion['pct_mayor_50']:.1f} %")

    # P3
    comparacion = comparar_promedio_e_indice(df, comparables)
    comparacion.to_csv(RESULTADOS_DIR / "p3_indice_por_comercio.csv", index=False)
    dif_sql = verificar_contra_sql(comparacion[["comercio", "indice_promedio"]])
    print("\n===== P3. PROMEDIO SIMPLE vs ÍNDICE RELATIVO POR COMERCIO =====")
    print(comparacion[["comercio", "promedio_simple", "indice_promedio",
                       "precios_comparados"]].round(3).to_string(index=False))

    indice_sucursal = indice_por(
        comparables, ["sucursal_id", "bandera_descripcion", "sucursal_nombre", "localidad", "comercio"])
    indice_sucursal.to_csv(RESULTADOS_DIR / "indice_por_sucursal.csv", index=False)

    if graficos:
        graficar(tabla_productos, comparacion, indice_sucursal, variacion)

    escribir_resumen(generales, n_comparables, variacion, canasta, ranking_variacion,
                     minimos_comercio, comparacion, indice_sucursal, extremos, dif_sql)
    print(f"\nResultados guardados en {RESULTADOS_DIR.relative_to(BASE_DIR)}/ (ver resumen.md)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de precios (Pandas + NumPy).")
    parser.add_argument("--sin-graficos", action="store_true", help="No generar los PNG.")
    args = parser.parse_args()
    main(graficos=not args.sin_graficos)
