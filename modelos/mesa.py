class Mesa:
    def __init__(self, numero, estado="libre", id_mesa=None):
        self._id_mesa = id_mesa
        self._numero = numero
        self._estado = estado

    @property
    def id_mesa(self):
        return self._id_mesa

    @property
    def numero(self):
        return self._numero

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in ("libre", "ocupada"):
            raise ValueError("Estado inválido para la mesa")
        self._estado = valor