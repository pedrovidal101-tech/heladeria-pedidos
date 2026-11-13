from datetime import datetime

class Pedido:
    def __init__(self, id_pedido, mesa, mesero):
        self.id_pedido = id_pedido
        self.mesa = mesa
        self.mesero = mesero
        self.productos = []  # Lista de productos agregados
        self.estado = "pendiente"  # pendiente, en preparacion, listo, entregado
        self.fecha_hora = datetime.now()

    def agregar_producto(self, producto):
        self.productos.append(producto)

    def calcular_total(self):
        return sum(producto.precio for producto in self.productos)

    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["pendiente", "en preparacion", "listo", "entregado"]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
        else:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido.")