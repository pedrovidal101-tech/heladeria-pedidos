class Producto:
    def __init__(self, nombre, categoria, precio, disponible=True, id_producto=None):
        self._id_producto = id_producto
        self._nombre = nombre
        self._categoria = categoria
        self._precio = precio
        self._disponible = disponible

    @property
    def id_producto(self):
        return self._id_producto

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if valor < 0:
            raise ValueError("El precio no puede ser negativo")
        self._precio = valor

    @property
    def nombre(self):
        return self._nombre

    def __str__(self):
        return f"{self._nombre} - ${self._precio:,.0f}"