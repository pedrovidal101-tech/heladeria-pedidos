from modelos.conexion import obtener_conexion


class PedidoDAO:
    ESTADOS_VALIDOS = ("pendiente", "en preparacion", "listo", "entregado", "cancelado")
    ESTADOS_ACTIVOS = ("pendiente", "en preparacion", "listo")

    @staticmethod
    def guardar_pedido(id_mesa, productos):
        """Inserta un pedido y sus productos. productos = [(id_producto, cantidad), ...]"""
        conn = obtener_conexion()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # 1. Insertar el pedido en estado 'pendiente'
            cursor.execute(
                "INSERT INTO Pedidos (id_mesa, estado) OUTPUT INSERTED.id_pedido VALUES (?, 'pendiente')",
                (id_mesa,)
            )
            id_pedido = cursor.fetchone()[0]

            # 2. Insertar cada producto en el detalle, tomando el precio de la BD
            for id_producto, cantidad in productos:
                cursor.execute(
                    """INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, precio_unitario)
                       SELECT ?, id_producto, ?, precio
                       FROM Productos
                       WHERE id_producto = ? AND disponible = 1""",
                    (id_pedido, cantidad, id_producto)
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Producto {id_producto} no existe o no está disponible")

            # 3. Marcar la mesa como ocupada
            cursor.execute(
                "UPDATE Mesas SET estado = 'ocupada' WHERE id_mesa = ?",
                (id_mesa,)
            )

            conn.commit()
            print(f" Pedido #{id_pedido} registrado exitosamente.")
            return id_pedido
        except Exception as ex:
            print(f" Error al guardar pedido: {ex}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def obtener_pedidos_pendientes():
        """Consulta los pedidos en estado 'pendiente' o 'en preparacion' para la cocina."""
        conn = obtener_conexion()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id_pedido, m.numero, p.estado, p.fecha_hora
                FROM Pedidos p
                JOIN Mesas m ON p.id_mesa = m.id_mesa
                WHERE p.estado IN ('pendiente', 'en preparacion')
                ORDER BY p.fecha_hora ASC
            """)
            return cursor.fetchall()
        except Exception as ex:
            print(f" Error al consultar pedidos: {ex}")
            return []
        finally:
            conn.close()

    @staticmethod
    def cambiar_estado(id_pedido, nuevo_estado):
        """Cambia el estado de un pedido y libera la mesa si ya no tiene pedidos activos."""
        if nuevo_estado not in PedidoDAO.ESTADOS_VALIDOS:
            print(f" Estado '{nuevo_estado}' no es válido.")
            return False

        conn = obtener_conexion()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Pedidos SET estado = ? WHERE id_pedido = ?",
                (nuevo_estado, id_pedido)
            )
            if cursor.rowcount == 0:
                print(f" El pedido #{id_pedido} no existe.")
                conn.rollback()
                return False

            if nuevo_estado not in PedidoDAO.ESTADOS_ACTIVOS:
                cursor.execute(
                    """UPDATE Mesas SET estado = 'libre'
                       WHERE id_mesa = (SELECT id_mesa FROM Pedidos WHERE id_pedido = ?)
                         AND NOT EXISTS (
                             SELECT 1 FROM Pedidos
                             WHERE id_mesa = (SELECT id_mesa FROM Pedidos WHERE id_pedido = ?)
                               AND estado IN ('pendiente', 'en preparacion', 'listo')
                         )""",
                    (id_pedido, id_pedido)
                )

            conn.commit()
            print(f" Pedido #{id_pedido} cambiado a '{nuevo_estado}'.")
            return True
        except Exception as ex:
            print(f" Error al actualizar estado: {ex}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def eliminar_o_cancelar_pedido(id_pedido):
        """Cancela un pedido (queda en la BD con estado 'cancelado') y libera la mesa."""
        return PedidoDAO.cambiar_estado(id_pedido, "cancelado")
    
    
    @staticmethod
    def obtener_pedido_por_id(id_pedido):
        """Busca un pedido por su número. Devuelve un diccionario o None si no existe."""
        conn = obtener_conexion()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.id_pedido, m.numero, p.estado, p.fecha_hora
                   FROM Pedidos p
                   JOIN Mesas m ON p.id_mesa = m.id_mesa
                   WHERE p.id_pedido = ?""",
                (id_pedido,)
            )
            fila = cursor.fetchone()
            if not fila:
                return None

            cursor.execute(
                """SELECT pr.nombre, d.cantidad, d.precio_unitario
                   FROM DetallePedido d
                   JOIN Productos pr ON d.id_producto = pr.id_producto
                   WHERE d.id_pedido = ?""",
                (id_pedido,)
            )
            productos = [
                {"nombre": n, "cantidad": c, "precio_unitario": float(p)}
                for n, c, p in cursor.fetchall()
            ]
            total = sum(p["cantidad"] * p["precio_unitario"] for p in productos)

            return {
                "id_pedido": fila[0],
                "mesa": fila[1],
                "estado": fila[2],
                "fecha_hora": fila[3],
                "productos": productos,
                "total": total,
            }
        except Exception as ex:
            print(f" Error al buscar pedido: {ex}")
            return None
        finally:
            conn.close()