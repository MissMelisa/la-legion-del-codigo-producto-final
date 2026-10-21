"""
Genera sql/datos_comercios.sql: un único script que crea la base,
las tablas, carga los datos y crea las vistas.

Lee los CSV de dataset/procesado/ (los genera limpieza.py). El script
resultante no depende de Python ni de archivos externos: se ejecuta
con `mysql -u root -p < sql/datos_comercios.sql` o desde Workbench
(File > Run SQL Script).

Uso:
    python preparacion/generar_sql.py
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESADO_DIR = BASE_DIR / "dataset" / "procesado"
SQL_SALIDA = BASE_DIR / "sql" / "datos_comercios.sql"

# Filas por sentencia INSERT (evita sentencias gigantes que superen
# max_allowed_packet en instalaciones con la configuración por defecto)
FILAS_POR_INSERT = 1000

# Un producto es "comparable" si tiene precio en al menos esta cantidad
# de sucursales. Debe coincidir con MIN_SUCURSALES de app/analisis.py.
MIN_SUCURSALES = 10


ESQUEMA = """
-- =========================================================
-- BASE DE DATOS: datos_comercios
-- Proyecto: La Legión del Código
-- Fuente: Precios Claros (SEPA), Córdoba, abril-mayo 2020
--
-- ARCHIVO GENERADO por preparacion/generar_sql.py: no editar a mano.
-- Crea la base desde cero (borra una versión anterior), las tablas,
-- carga los datos y crea las vistas.
-- =========================================================

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS datos_comercios;

CREATE DATABASE datos_comercios
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE datos_comercios;


-- =========================================================
-- TABLAS
-- =========================================================

CREATE TABLE productos (
    id VARCHAR(50) NOT NULL,
    marca VARCHAR(150),
    nombre VARCHAR(255),
    presentacion VARCHAR(100),
    categoria_1 VARCHAR(150),
    categoria_2 VARCHAR(150),
    categoria_3 VARCHAR(150),

    PRIMARY KEY (id)
);

CREATE TABLE sucursales (
    id VARCHAR(50) NOT NULL,
    comercio_id BIGINT,
    bandera_id BIGINT,
    bandera_descripcion VARCHAR(255),
    comercio_razon_social VARCHAR(255),
    provincia VARCHAR(10),
    localidad VARCHAR(255),
    direccion VARCHAR(500),
    lat DECIMAL(10,7),
    lng DECIMAL(10,7),
    sucursal_nombre VARCHAR(255),
    sucursal_tipo VARCHAR(100),

    PRIMARY KEY (id)
);

-- Un único precio vigente por producto y sucursal (clave compuesta)
CREATE TABLE precios (
    precio DECIMAL(12,2) NOT NULL,
    producto_id VARCHAR(50) NOT NULL,
    sucursal_id VARCHAR(50) NOT NULL,

    PRIMARY KEY (producto_id, sucursal_id),

    INDEX idx_precios_sucursal (sucursal_id),

    CONSTRAINT fk_precios_producto
        FOREIGN KEY (producto_id)
        REFERENCES productos(id),

    CONSTRAINT fk_precios_sucursal
        FOREIGN KEY (sucursal_id)
        REFERENCES sucursales(id),

    CONSTRAINT chk_precio_positivo CHECK (precio > 0)
);
"""


VISTAS = f"""
-- =========================================================
-- VISTAS
-- =========================================================

-- Integra productos, sucursales y precios (la usa el menú).
CREATE VIEW vista_precios_detalle AS
SELECT
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.presentacion,
    p.categoria_1,
    p.categoria_2,
    p.categoria_3,
    pr.precio,
    s.id AS sucursal_id,
    s.sucursal_nombre,
    s.bandera_descripcion,
    s.comercio_razon_social,
    s.localidad,
    s.provincia
FROM precios pr
INNER JOIN productos p
    ON pr.producto_id = p.id
INNER JOIN sucursales s
    ON pr.sucursal_id = s.id;


-- Pregunta 2: diferencia entre precio máximo y mínimo de cada
-- producto. Se agrupa por producto_id (no por nombre: hay nombres
-- repetidos que corresponden a productos distintos).
CREATE VIEW vista_resumen_producto AS
SELECT
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.presentacion,
    COUNT(*) AS cantidad_sucursales,
    COUNT(DISTINCT s.comercio_razon_social) AS cantidad_comercios,
    MIN(pr.precio) AS precio_minimo,
    MAX(pr.precio) AS precio_maximo,
    ROUND(AVG(pr.precio), 2) AS precio_promedio,
    MAX(pr.precio) - MIN(pr.precio) AS diferencia_precio,
    ROUND((MAX(pr.precio) - MIN(pr.precio)) / MIN(pr.precio) * 100, 2)
        AS variacion_porcentual
FROM precios pr
INNER JOIN productos p
    ON pr.producto_id = p.id
INNER JOIN sucursales s
    ON pr.sucursal_id = s.id
GROUP BY p.id, p.nombre, p.marca, p.presentacion;


-- Pregunta 1: precio mínimo de cada producto y comercio donde se
-- encuentra. Si varios comercios empatan en el mínimo, aparece una
-- fila por comercio.
CREATE VIEW vista_precio_minimo_producto AS
SELECT
    producto_id,
    producto,
    precio AS precio_minimo,
    comercio_razon_social AS comercio,
    COUNT(*) AS sucursales_con_minimo
FROM (
    SELECT
        d.*,
        MIN(d.precio) OVER (PARTITION BY d.producto_id) AS minimo_producto
    FROM vista_precios_detalle d
) t
WHERE precio = minimo_producto
GROUP BY producto_id, producto, precio, comercio_razon_social;


-- Pregunta 3 (corregida): en vez del promedio simple por comercio
-- (que compara surtidos distintos), cada precio se divide por el
-- precio promedio de ESE producto entre todas las sucursales.
-- 1,00 = precio promedio; 1,10 = 10 % más caro que el promedio.
-- Solo productos comparables (>= {MIN_SUCURSALES} sucursales).
CREATE VIEW vista_indice_precio AS
SELECT
    producto_id,
    producto,
    sucursal_id,
    sucursal_nombre,
    bandera_descripcion,
    comercio_razon_social,
    localidad,
    precio,
    precio / AVG(precio) OVER (PARTITION BY producto_id) AS indice
FROM (
    SELECT
        d.*,
        COUNT(*) OVER (PARTITION BY d.producto_id) AS cantidad_sucursales
    FROM vista_precios_detalle d
) t
WHERE cantidad_sucursales >= {MIN_SUCURSALES};


CREATE VIEW vista_indice_comercio AS
SELECT
    comercio_razon_social AS comercio,
    COUNT(DISTINCT sucursal_id) AS sucursales,
    COUNT(DISTINCT producto_id) AS productos_comparados,
    COUNT(*) AS precios_comparados,
    ROUND(AVG(indice), 4) AS indice_promedio
FROM vista_indice_precio
GROUP BY comercio_razon_social;


CREATE VIEW vista_indice_sucursal AS
SELECT
    sucursal_id,
    bandera_descripcion,
    sucursal_nombre,
    localidad,
    comercio_razon_social AS comercio,
    COUNT(*) AS productos_comparados,
    ROUND(AVG(indice), 4) AS indice_promedio
FROM vista_indice_precio
GROUP BY sucursal_id, bandera_descripcion, sucursal_nombre,
         localidad, comercio_razon_social;


-- =========================================================
-- VERIFICACIÓN
-- =========================================================

SELECT 'productos' AS tabla, COUNT(*) AS cantidad FROM productos
UNION ALL
SELECT 'sucursales', COUNT(*) FROM sucursales
UNION ALL
SELECT 'precios', COUNT(*) FROM precios;
"""


def valor_sql(valor):
    """Convierte un valor de pandas en un literal SQL."""
    if pd.isna(valor) or valor == "":
        return "NULL"
    if isinstance(valor, (int, float)):
        return repr(valor)
    texto = str(valor).replace("\\", "\\\\").replace("'", "''")
    return f"'{texto}'"


def inserts(tabla, df):
    columnas = ", ".join(df.columns)
    filas = [
        "(" + ", ".join(valor_sql(v) for v in fila) + ")"
        for fila in df.itertuples(index=False)
    ]
    bloques = []
    for inicio in range(0, len(filas), FILAS_POR_INSERT):
        lote = ",\n".join(filas[inicio:inicio + FILAS_POR_INSERT])
        bloques.append(f"INSERT INTO {tabla} ({columnas}) VALUES\n{lote};")
    return f"\n-- {tabla}: {len(df)} filas\n" + "\n\n".join(bloques) + "\n"


def leer(nombre, numericas=()):
    df = pd.read_csv(
        PROCESADO_DIR / nombre, dtype=str, keep_default_na=False,
        encoding="utf-8",
    )
    for columna in numericas:
        df[columna] = pd.to_numeric(df[columna]).astype(object)
    return df


def main():
    productos = leer("productos_cordoba.csv")
    sucursales = leer("sucursales_cordoba.csv")
    precios = leer("precios_cordoba.csv", numericas=["precio"])

    # Integridad: todo precio debe referenciar un producto y una
    # sucursal existentes (si no, el INSERT fallaría por la FK)
    huerfanos = (
        ~precios["producto_id"].isin(productos["id"])
        | ~precios["sucursal_id"].isin(sucursales["id"])
    ).sum()
    if huerfanos:
        raise ValueError(f"{huerfanos} precios sin producto o sucursal")

    sucursales = sucursales[[
        "id", "comercio_id", "bandera_id", "bandera_descripcion",
        "comercio_razon_social", "provincia", "localidad", "direccion",
        "lat", "lng", "sucursal_nombre", "sucursal_tipo",
    ]]
    precios = precios[["precio", "producto_id", "sucursal_id"]]

    contenido = (
        ESQUEMA
        + "\n-- =========================================================\n"
        + "-- DATOS\n"
        + "-- =========================================================\n"
        + inserts("productos", productos)
        + inserts("sucursales", sucursales)
        + inserts("precios", precios)
        + VISTAS
    )
    SQL_SALIDA.parent.mkdir(exist_ok=True)
    SQL_SALIDA.write_text(contenido, encoding="utf-8")

    print(f"Generado {SQL_SALIDA.relative_to(BASE_DIR)}")
    print(f"  productos:  {len(productos)}")
    print(f"  sucursales: {len(sucursales)}")
    print(f"  precios:    {len(precios)}")


if __name__ == "__main__":
    main()
