"""
Conexion a la base de datos MySQL usando PyMySQL.

Los datos de conexión se leen del archivo .env en la raíz del
proyecto (ver .env.ejemplo).
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def crear_engine():
    """Engine de SQLAlchemy con la misma configuración que ConexionBD,
    para leer consultas directo a un DataFrame (pd.read_sql)."""
    from sqlalchemy import create_engine

    bd = ConexionBD()
    return create_engine(
        f"mysql+pymysql://{bd.user}:{quote_plus(bd.password)}"
        f"@{bd.host}:{bd.port}/{bd.database}?charset=utf8mb4"
    )


class ConexionBD:
    """Maneja la conexión a MySQL y la ejecucion de  las consultas."""

    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.port = int(port or os.getenv("MYSQL_PORT", "3306"))
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password or os.getenv("MYSQL_PASSWORD", "")
        self.database = database or os.getenv("MYSQL_DATABASE", "datos_comercios")
        self.conexion = None

    def conectar(self):
        """Abre la conexión si todavía no está abierta y la devuelve."""
        if self.conexion is None or not self.conexion.open:
            self.conexion = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                #necesito esto por que la base lo usa. 
                charset="utf8mb4",
                # necesario para que cada fila sea un dict
                cursorclass=pymysql.cursors.DictCursor,
            )
        return self.conexion

    def cerrar(self):
        if self.conexion is not None and self.conexion.open:
            self.conexion.close()
            self.conexion = None

    def ejecutar_consulta(self, sql, parametros=None):
        """SELECT: devuelve una lista de diccionarios (una por fila)."""
        conexion = self.conectar()
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros or ())
            return cursor.fetchall()

    def ejecutar_accion(self, sql, parametros=None):
        """INSERT / UPDATE / DELETE: hace commit y devuelve filas afectadas."""
        conexion = self.conectar()
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros or ())
            filas_afectadas = cursor.rowcount
        conexion.commit()
        return filas_afectadas

    def ejecutar_transaccion(self, operaciones):
        """Ejecuta varias acciones (INSERT/UPDATE/DELETE) como una única
        transacción: si alguna falla, se hace rollback de todas.

        `operaciones` es una lista de tuplas (sql, parametros).
        Devuelve la suma de filas afectadas.
        """
        conexion = self.conectar()
        try:
            with conexion.cursor() as cursor:
                total_afectadas = 0
                for sql, parametros in operaciones:
                    cursor.execute(sql, parametros or ())
                    total_afectadas += cursor.rowcount
            conexion.commit()
            return total_afectadas
        except Exception:
            conexion.rollback()
            raise

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()
