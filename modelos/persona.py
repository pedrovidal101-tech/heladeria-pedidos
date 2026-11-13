class Persona:
    def __init__(self, id_persona, nombre, cedula):
        self.id_persona = id_persona
        self.nombre = nombre
        self.cedula = cedula


class Empleado(Persona):
    def __init__(self, id_persona, nombre, cedula, rol):
        super().__init__(id_persona, nombre, cedula)
        self.rol = rol


class Mesero(Empleado):
    def __init__(self, id_persona, nombre, cedula):
        super().__init__(id_persona, nombre, cedula, "Mesero")

    def tomar_pedido(self, mesa, productos):
        return f"Mesero {self.nombre} tomó pedido en mesa {mesa.numero}"


class Cocinero(Empleado):
    def __init__(self, id_persona, nombre, cedula):
        super().__init__(id_persona, nombre, cedula, "Cocinero")

    def preparar_pedido(self, id_pedido):
        return f"Cocinero {self.nombre} preparando pedido #{id_pedido}"