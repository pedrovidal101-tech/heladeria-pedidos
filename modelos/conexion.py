import os
import pyodbc


def obtener_conexion():
    try:
        conexion = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=HeladeriaDB;"
            "UID=sa;"
            f"PWD={os.getenv('DB_PASSWORD', '')};"
            "TrustServerCertificate=yes;"
        )
        return conexion
    except Exception as ex:
        print(f"Error al conectar a SQL Server: {ex}")
        return None