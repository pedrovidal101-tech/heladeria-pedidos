from modelos.conexion import obtener_conexion


class ProductoDAO:
    @staticmethod
    def obtener_disponibles():
        """Devuelve [(id_producto, nombre, precio), ...] de los productos disponibles."""
        conn = obtener_conexion()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_producto, nombre, precio FROM Productos "
                "WHERE disponible = 1 ORDER BY nombre"
            )
            return cursor.fetchall()
        except Exception as ex:
            print(f" Error al consultar productos: {ex}")
            return []
        finally:
            conn.close()